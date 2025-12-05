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
    <Card isCompact className="metadata-viewer-card">
      <CardTitle className="metadata-viewer-title">
        <InfoCircleIcon className="metadata-viewer-icon" />
        LLM Component Selection Reasoning
      </CardTitle>
      <CardBody>
        <DescriptionList isCompact isHorizontal className="metadata-viewer-list">
          {metadata.componentType && (
            <DescriptionListGroup>
              <DescriptionListTerm className="metadata-viewer-term">Component Type</DescriptionListTerm>
              <DescriptionListDescription>
                <Label color="blue" className="metadata-viewer-label">{metadata.componentType}</Label>
              </DescriptionListDescription>
            </DescriptionListGroup>
          )}
          {metadata.reason && (
            <DescriptionListGroup>
              <DescriptionListTerm className="metadata-viewer-term">Reason</DescriptionListTerm>
              <DescriptionListDescription className="metadata-viewer-description">
                {metadata.reason}
              </DescriptionListDescription>
            </DescriptionListGroup>
          )}
          {metadata.confidence && (
            <DescriptionListGroup>
              <DescriptionListTerm className="metadata-viewer-term">Confidence</DescriptionListTerm>
              <DescriptionListDescription>
                <Label 
                  color={
                    parseInt(metadata.confidence) >= 90 ? 'green' : 
                    parseInt(metadata.confidence) >= 70 ? 'orange' : 
                    'red'
                  }
                  className="metadata-viewer-label"
                >
                  {metadata.confidence}
                </Label>
              </DescriptionListDescription>
            </DescriptionListGroup>
          )}
          {metadata.strategy && (
            <DescriptionListGroup>
              <DescriptionListTerm className="metadata-viewer-term">Selection Strategy</DescriptionListTerm>
              <DescriptionListDescription>
                <Label color="teal" className="metadata-viewer-label">{metadata.strategy}</Label>
              </DescriptionListDescription>
            </DescriptionListGroup>
          )}
        </DescriptionList>
      </CardBody>
    </Card>
  );
};

