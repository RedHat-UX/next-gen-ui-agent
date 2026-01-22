import { Card, CardBody, CardTitle, Label } from '@patternfly/react-core';

/**
 * Extract the data key from a JSONPath data_path.
 * Examples: "$.pods[*].cpu_usage" -> "cpu_usage", "$.nodes[*].memory" -> "memory"
 */
function extractDataKeyFromPath(dataPath: string): string | null {
  if (!dataPath) return null;
  
  // Remove JSONPath prefix ($, $., $..)
  const path = dataPath.replace(/^\$\.?\.?/, '');
  
  // Split by dots and get the last part
  const parts = path.split('.');
  if (parts.length === 0) return null;
  
  // Get the last part (the actual field key)
  const lastPart = parts[parts.length - 1];
  
  // Remove array indices like [*], [0], [1], etc.
  const dataKey = lastPart.replace(/\[.*?\]/g, '');
  
  return dataKey || null;
}

interface DataTransformationViewerProps {
  dataTransform: {
    transformerName?: string;
    jsonWrappingField?: string;
    inlineSource?: string;
    inlineRecordCount?: number;
    fieldCount?: number;
    inputDataType?: string;
    configMappings?: Record<string, string>;
    fields?: Array<{
      name: string;
      dataPath: string;
      formatter?: string;
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
          {dataTransform.inputDataType && (
            <div>
              <strong className="data-transform-label-title">
                Data Type:{' '}
              </strong>
              <span className="data-transform-label-badge">
                {dataTransform.inputDataType}
              </span>
            </div>
          )}
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
                {dataTransform.fields.map((field, idx) => {
                  const formatter = field.formatter;
                  // Extract data key from dataPath to match against configMappings
                  const dataKey = extractDataKeyFromPath(field.dataPath);
                  const isOverridden = dataTransform.configMappings && 
                    dataKey && 
                    dataTransform.configMappings[dataKey] === formatter;
                  
                  return (
                    <div 
                      key={`${messageId}-field-${idx}`}
                      className="data-transform-field-item"
                    >
                      <div className="data-transform-field-name-wrapper">
                        <strong className="data-transform-field-name">
                          {field.name}
                        </strong>
                      </div>
                      {formatter && (
                        <div style={{ marginTop: '4px', display: 'flex', alignItems: 'center', gap: '8px' }}>
                          <span className="data-transform-label-title" style={{ fontSize: '11px' }}>
                            Formatter:
                          </span>
                          <Label 
                            color={isOverridden ? "teal" : "green"} 
                            isCompact 
                            title={isOverridden ? `Formatter override: ${formatter}` : `Formatter: ${formatter}`}
                          >
                            {formatter}
                          </Label>
                          {isOverridden && (
                            <span style={{ fontSize: '10px', color: '#666', fontStyle: 'italic' }}>
                              (override)
                            </span>
                          )}
                        </div>
                      )}
                      <div style={{ marginTop: '4px' }}>
                        <span className="data-transform-label-title" style={{ fontSize: '11px' }}>
                          Path:
                        </span>
                        <code className="data-transform-field-path" style={{ marginLeft: '8px' }}>
                          {field.dataPath}
                        </code>
                      </div>
                    </div>
                  );
                })}
              </div>
            </div>
          )}
        </div>
      </CardBody>
    </Card>
  );
}
