// Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
// SPDX-License-Identifier: Apache-2.0
import { Construct } from 'constructs';
import { ControlRunbookDocument, ControlRunbookProps, RemediationScope } from './control_runbook';
import { PlaybookProps } from '../lib/control_runbooks-construct';
import { HardCodedString } from '@cdklabs/cdk-ssm-documents';

export function createControlRunbook(scope: Construct, id: string, props: PlaybookProps): ControlRunbookDocument {
  return new DisablePublicIPv4Addresses(scope, id, { ...props, controlId: 'EC2.9' });
}

export class DisablePublicIPv4Addresses extends ControlRunbookDocument {
  constructor(scope: Construct, id: string, props: ControlRunbookProps) {
    super(scope, id, {
      ...props,
      securityControlId: 'EC2.9',
      remediationName: 'DisablePublicIPv4Addresses',
      scope: RemediationScope.GLOBAL,
      resourceIdName: 'InstanceId',
      updateDescription: HardCodedString.of('removed public ip'),
    });
  }
}
