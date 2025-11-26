import { Card, CardBody, CardTitle } from '@patternfly/react-core';

interface DataTransformationViewerProps {
  dataTransform: {
    transformerName?: string;
    jsonWrappingField?: string;
    inlineSource?: string;
    inlineRecordCount?: number;
    fieldCount?: number;
    fields?: Array<{
      name: string;
      dataPath: string;
    }>;
  };
  messageId: string;
}

export function DataTransformationViewer({ dataTransform, messageId }: DataTransformationViewerProps) {
  return (
    <Card className="data-transform-card">
      <CardTitle className="data-transform-title">
        <div className="data-transform-title-wrapper">
          <span className="data-transform-emoji">🔄</span>
          <strong>Data Transformation</strong>
        </div>
      </CardTitle>
      <CardBody className="data-transform-body">
        <div className="data-transform-content">
          {dataTransform.transformerName && (
            <div>
              <strong className="data-transform-label-title">
                Input Transformer:{' '}
              </strong>
              <span className="data-transform-label-badge">
                {dataTransform.transformerName}
              </span>
            </div>
          )}
          
          {dataTransform.jsonWrappingField && (
            <div>
              <strong className="data-transform-label-title">
                JSON Wrapping Field:{' '}
              </strong>
              <span className="data-transform-label-badge-wrapping">
                {dataTransform.jsonWrappingField}
              </span>
            </div>
          )}
          {dataTransform.inlineSource && (
            <div>
              <strong className="data-transform-label-title">
                Inline Dataset:{' '}
              </strong>
              <span className="data-transform-label-badge">
                {dataTransform.inlineSource}
              </span>
              {typeof dataTransform.inlineRecordCount === 'number' && (
                <span className="data-transform-inline-note">
                  {` (${dataTransform.inlineRecordCount} records)`}
                </span>
              )}
            </div>
          )}
          {dataTransform.fields && dataTransform.fields.length > 0 && (
            <div className="data-transform-fields-section">
              <strong className="data-transform-fields-title">
                Fields Extracted ({dataTransform.fields.length}):
              </strong>
              <div className="data-transform-fields-list">
                {dataTransform.fields.map((field, idx) => (
                  <div 
                    key={`${messageId}-field-${idx}`}
                    className="data-transform-field-item"
                  >
                    <div className="data-transform-field-name-wrapper">
                      <strong className="data-transform-field-name">
                        {field.name}
                      </strong>
                    </div>
                    <code className="data-transform-field-path">
                      {field.dataPath}
                    </code>
                  </div>
                ))}
              </div>
            </div>
          )}
        </div>
      </CardBody>
    </Card>
  );
}
