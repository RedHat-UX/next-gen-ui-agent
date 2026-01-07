import React from 'react';
import { JsonViewer } from './JsonViewer';

interface DatasetViewerProps {
  dataset: any;
  messageId: string;
}

export function DatasetViewer({ dataset, messageId }: DatasetViewerProps) {
  if (!dataset) {
    return null;
  }

  return (
    <div className="dataset-viewer-container" style={{ marginTop: '16px' }}>
      <div className="dataset-viewer-content">
        <p className="dataset-viewer-description">
          This dataset was attached to the request and used by the LLM to generate the component.
        </p>
        <JsonViewer 
          config={dataset} 
          messageId={`${messageId}-dataset`} 
          alwaysExpanded={true}
        />
      </div>
    </div>
  );
}

