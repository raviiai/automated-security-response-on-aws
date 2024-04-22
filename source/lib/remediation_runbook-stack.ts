// Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
// SPDX-License-Identifier: Apache-2.0

//
// Remediation Runbook Stack - installs non standard-specific remediation
// runbooks that are used by one or more standards
//
import * as cdk from 'aws-cdk-lib';
import {
  PolicyStatement,
 
  Effect,
 
  Policy,
 
  CfnPolicy,

} from 'aws-cdk-lib/aws-iam';
import { OrchestratorMemberRole } from './orchestrator_roles-construct';
import AdminAccountParam from './admin-account-param';

import { RunbookFactory } from './runbook_factory';

import { SsmRole } from './ssmplaybook';
import { Aspects, CfnParameter } from 'aws-cdk-lib';
import { WaitProvider } from './wait-provider';
import SsmDocRateLimit from './ssm-doc-rate-limit';

export interface MemberRoleStackProps extends cdk.StackProps {
  readonly solutionId: string;
  readonly solutionVersion: string;
  readonly solutionDistBucket: string;
}

export class MemberRoleStack extends cdk.Stack {
  _orchestratorMemberRole: OrchestratorMemberRole;

  constructor(scope: cdk.App, id: string, props: MemberRoleStackProps) {
    super(scope, id, props);
    /********************
     ** Parameters
     ********************/
    const RESOURCE_PREFIX = props.solutionId.replace(/^DEV-/, ''); // prefix on every resource name
    const adminRoleName = `${RESOURCE_PREFIX}-SHARR-Orchestrator-Admin`;

    const adminAccount = new AdminAccountParam(this, 'AdminAccountParameter');
    this._orchestratorMemberRole = new OrchestratorMemberRole(this, 'OrchestratorMemberRole', {
      solutionId: props.solutionId,
      adminAccountId: adminAccount.value,
      adminRoleName: adminRoleName,
    });
  }

  getOrchestratorMemberRole(): OrchestratorMemberRole {
    return this._orchestratorMemberRole;
  }
}

export interface StackProps extends cdk.StackProps {
  readonly solutionId: string;
  readonly solutionVersion: string;
  readonly solutionDistBucket: string;
  ssmdocs?: string;
  roleStack: MemberRoleStack;
}

export class RemediationRunbookStack extends cdk.Stack {
  constructor(scope: cdk.App, id: string, props: StackProps) {
    super(scope, id, props);

    const waitProviderServiceTokenParam = new CfnParameter(this, 'WaitProviderServiceToken');

    const waitProvider = WaitProvider.fromServiceToken(
      this,
      'WaitProvider',
      waitProviderServiceTokenParam.valueAsString,
    );

    Aspects.of(this).add(new SsmDocRateLimit(waitProvider));

    let ssmdocs = '';
    if (props.ssmdocs == undefined) {
      ssmdocs = '../remediation_runbooks';
    } else {
      ssmdocs = props.ssmdocs;
    }

    const RESOURCE_PREFIX = props.solutionId.replace(/^DEV-/, ''); // prefix on every resource name
    const remediationRoleNameBase = `${RESOURCE_PREFIX}-`;

    //-----------------------
    // DisableUnrestrictedAccessToHighRiskPorts
    //
    {
      const remediationName = 'DisableUnrestrictedAccessToHighRiskPorts';
      const inlinePolicy = new Policy(props.roleStack, `ASR-Remediation-Policy-${remediationName}`);

      const remediationPolicy = new PolicyStatement();
      remediationPolicy.addActions('ec2:DescribeSecurityGroupRules', 'ec2:RevokeSecurityGroupIngress');
      remediationPolicy.effect = Effect.ALLOW;
      remediationPolicy.addResources('*');
      inlinePolicy.addStatements(remediationPolicy);

      new SsmRole(props.roleStack, 'RemediationRole ' + remediationName, {
        solutionId: props.solutionId,
        ssmDocName: remediationName,
        remediationPolicy: inlinePolicy,
        remediationRoleName: `${remediationRoleNameBase}${remediationName}`,
      });

      RunbookFactory.createRemediationRunbook(this, 'ASR ' + remediationName, {
        ssmDocName: remediationName,
        ssmDocPath: ssmdocs,
        ssmDocFileName: `${remediationName}.yaml`,
        scriptPath: `${ssmdocs}/scripts`,
        solutionVersion: props.solutionVersion,
        solutionDistBucket: props.solutionDistBucket,
        solutionId: props.solutionId,
      });
      const childToMod = inlinePolicy.node.findChild('Resource') as CfnPolicy;
      childToMod.cfnOptions.metadata = {
        cfn_nag: {
          rules_to_suppress: [
            {
              id: 'W12',
              reason: 'Resource * is required for to allow remediation for any resource.',
            },
          ],
        },
      };
    }
   

    //-----------------------
    // DisablePublicIPv4Addresses
    //
    {
      const remediationName = 'DisablePublicIPv4Addresses';
      const inlinePolicy = new Policy(props.roleStack, `ASR-Remediation-Policy-${remediationName}`);

      const remediationPolicy = new PolicyStatement();
      remediationPolicy.addActions("ec2:AllocateAddress",
      "ec2:AssociateAddress",
      "ec2:CreateNetworkInterface",
      "ec2:AttachNetworkInterface",
      "ec2:DescribeInstances",
      "ec2:DescribeNetworkInterfaces",
      "ec2:ReleaseAddress",
      "ec2:DeleteNetworkInterface",
      "ec2:DetachNetworkInterface");

      remediationPolicy.effect = Effect.ALLOW;
      remediationPolicy.addResources('*');
      inlinePolicy.addStatements(remediationPolicy);

      new SsmRole(props.roleStack, 'RemediationRole ' + remediationName, {
        solutionId: props.solutionId,
        ssmDocName: remediationName,
        remediationPolicy: inlinePolicy,
        remediationRoleName: `${remediationRoleNameBase}${remediationName}`,
      });

      RunbookFactory.createRemediationRunbook(this, 'ASR ' + remediationName, {
        ssmDocName: remediationName,
        ssmDocPath: ssmdocs,
        ssmDocFileName: `${remediationName}.yaml`,
        scriptPath: `${ssmdocs}/scripts`,
        solutionVersion: props.solutionVersion,
        solutionDistBucket: props.solutionDistBucket,
        solutionId: props.solutionId,
      });
      const childToMod = inlinePolicy.node.findChild('Resource') as CfnPolicy;
      childToMod.cfnOptions.metadata = {
        cfn_nag: {
          rules_to_suppress: [
            {
              id: 'W12',
              reason: 'Resource * is required for to allow remediation for any resource.',
            },
          ],
        },
      };
    }

// ###################################################################


  }
}
