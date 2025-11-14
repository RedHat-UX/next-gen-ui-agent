import React from 'react';
import {
  Card,
  CardBody,
  CardTitle,
  DescriptionList,
  DescriptionListGroup,
  DescriptionListTerm,
  DescriptionListDescription,
  Label,
} from '@patternfly/react-core';
import { InfoCircleIcon } from '@patternfly/react-icons';

interface Metadata {
  componentType?: string;
  reason?: string;
  confidence?: string;
  strategy?: string;
}

interface MetadataViewerProps {
  metadata: Metadata;
  messageId: string;
}

export const MetadataViewer: React.FC<MetadataViewerProps> = ({ metadata }) => {
  if (!metadata || Object.keys(metadata).length === 0) {
    return null;
  }

  return (
    <Card isCompact style={{ marginTop: '1rem', backgroundColor: '#f5f5f5' }}>
      <CardTitle>
        <InfoCircleIcon style={{ marginRight: '0.5rem', color: '#06c' }} />
        LLM Component Selection Reasoning
      </CardTitle>
      <CardBody>
        <DescriptionList isCompact isHorizontal>
          {metadata.componentType && (
            <DescriptionListGroup>
              <DescriptionListTerm>Component Type</DescriptionListTerm>
              <DescriptionListDescription>
                <Label color="blue">{metadata.componentType}</Label>
              </DescriptionListDescription>
            </DescriptionListGroup>
          )}
          {metadata.reason && (
            <DescriptionListGroup>
              <DescriptionListTerm>Reason</DescriptionListTerm>
              <DescriptionListDescription>
                {metadata.reason}
              </DescriptionListDescription>
            </DescriptionListGroup>
          )}
          {metadata.confidence && (
            <DescriptionListGroup>
              <DescriptionListTerm>Confidence</DescriptionListTerm>
              <DescriptionListDescription>
                <Label color={
                  parseInt(metadata.confidence) >= 90 ? 'green' : 
                  parseInt(metadata.confidence) >= 70 ? 'orange' : 
                  'red'
                }>
                  {metadata.confidence}
                </Label>
              </DescriptionListDescription>
            </DescriptionListGroup>
          )}
          {metadata.strategy && (
            <DescriptionListGroup>
              <DescriptionListTerm>Selection Strategy</DescriptionListTerm>
              <DescriptionListDescription>
                <Label color="teal">{metadata.strategy}</Label>
              </DescriptionListDescription>
            </DescriptionListGroup>
          )}
        </DescriptionList>
      </CardBody>
    </Card>
  );
};

