import React, { useState } from 'react';
import {
  Card,
  CardBody,
  CardTitle,
  Button,
  TextArea,
  FormGroup,
  Alert,
  FormSelect,
  FormSelectOption
} from '@patternfly/react-core';

interface ChartConfig {
  component: string;
  id: string;
  title: string;
  chartType: string;
  data: unknown[];
  [key: string]: unknown;
}

interface PrometheusConverterProps {
  onConvert: (config: ChartConfig) => void;
}

export const PrometheusConverter: React.FC<PrometheusConverterProps> = ({ onConvert }) => {
  const [prometheusData, setPrometheusData] = useState('');
  const [error, setError] = useState<string | null>(null);
  const [title, setTitle] = useState('Prometheus Metrics');
  const [chartType, setChartType] = useState<'line' | 'bar'>('line');
  const [downsample, setDownsample] = useState('1');

  const handleConvert = async () => {
    setError(null);
    
    if (!prometheusData.trim()) {
      setError('Please paste Prometheus data');
      return;
    }

    try {
      // Call backend to test the actual Prometheus transformer
      const response = await fetch(`${import.meta.env.VITE_API_ENDPOINT.replace('/generate', '')}/test-prometheus`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          prometheusData: prometheusData,
          userPrompt: `Show ${title} as a ${chartType} chart`,
          strategy: 'one-step',
          downsample: parseInt(downsample) || 1
        })
      });

      const result = await response.json();
      
      if (result.error) {
        setError(`Backend error: ${result.error} - ${result.details || ''}`);
        return;
      }

      if (!result.response) {
        setError('Backend returned no component configuration');
        return;
      }
      
      // Pass the backend-generated config to the parent
      onConvert(result.response);
      setError(null);
    } catch (err) {
      setError(`Conversion failed: ${err instanceof Error ? err.message : 'Unknown error'}`);
    }
  };

  const exampleData = `{
  "result": [{
    "metric": {
      "__name__": "instance:node_cpu_utilisation:rate1m",
      "container": "kube-rbac-proxy",
      "endpoint": "https",
      "instance": "ip-10-0-18-210.ec2.internal",
      "job": "node-exporter",
      "managed_cluster": "fb096bb9-04da-4b73-bdfc-5bf2716f0b39",
      "namespace": "openshift-monitoring",
      "pod": "node-exporter-zv64p",
      "prometheus": "openshift-monitoring/k8s",
      "service": "node-exporter"
    },
    "values": [
      [1763032771.933, "0.051437499999995695"],
      [1763032831.933, "0.0499583333333351"],
      [1763032891.933, "0.0639791666666858"],
      [1763032951.933, "0.05218750000000849"],
      [1763033011.933, "0.056708333333336136"],
      [1763033071.933, "0.05020833333333119"],
      [1763033131.933, "0.047354166666664144"],
      [1763033191.933, "0.057354166666664486"],
      [1763033251.933, "0.07220833333333931"],
      [1763033311.933, "0.06304166666666267"],
      [1763033371.933, "0.0496041666666589"],
      [1763033431.933, "0.0540416666666631"],
      [1763033491.933, "0.05816666666666526"],
      [1763033551.933, "0.06195833333334333"],
      [1763033611.933, "0.07622916666666257"],
      [1763033671.933, "0.04985416666666853"],
      [1763033731.933, "0.05227083333333682"],
      [1763033791.933, "0.08566666666666878"],
      [1763033851.933, "0.07541666666666935"],
      [1763033911.933, "0.05654166666667115"],
      [1763033971.933, "0.047041666666662874"],
      [1763034031.933, "0.050249999999994466"],
      [1763034091.933, "0.04933333333331902"],
      [1763034151.933, "0.0543958333333312"],
      [1763034211.933, "0.12995833333331797"],
      [1763034271.933, "0.0489791666666648"],
      [1763034331.933, "0.062270833333340825"],
      [1763034391.933, "0.05181250000000803"],
      [1763034451.933, "0.056229166666673214"],
      [1763034511.933, "0.07941666666665692"],
      [1763034571.933, "0.04864583333332362"],
      [1763034631.933, "0.05777083333333011"],
      [1763034691.933, "0.05152083333332225"],
      [1763034751.933, "0.052395833333339525"],
      [1763034811.933, "0.0683124999999899"],
      [1763034871.933, "0.05449999999999944"],
      [1763034931.933, "0.057604166666666456"],
      [1763034991.933, "0.053083333333336924"],
      [1763035051.933, "0.051437499999992364"],
      [1763035111.933, "0.06222916666666001"],
      [1763035171.933, "0.05585416666666121"],
      [1763035231.933, "0.05479166666667168"],
      [1763035291.933, "0.06695833333332502"],
      [1763035351.933, "0.04918749999998884"],
      [1763035411.933, "0.06189583333332194"],
      [1763035471.933, "0.057416666666674776"],
      [1763035531.933, "0.08770833333333072"],
      [1763035591.933, "0.05108333333333481"],
      [1763035651.933, "0.050229166666671876"],
      [1763035711.933, "0.059916666666668394"],
      [1763035771.933, "0.05364583333333317"],
      [1763035831.933, "0.04820833333333807"],
      [1763035891.933, "0.061312499999990444"],
      [1763035951.933, "0.04927083333334015"],
      [1763036011.933, "0.09112500000000212"],
      [1763036071.933, "0.05593750000001152"],
      [1763036131.933, "0.05602083333333352"],
      [1763036191.933, "0.08164583333332487"],
      [1763036251.933, "0.047354166666664144"],
      [1763036311.933, "0.06516666666667048"],
      [1763036371.933, "0.0762083333333361"]
    ]
  }],
  "resultType": "matrix"
}`;

  return (
    <Card>
      <CardTitle>Prometheus Data Converter (Backend Test)</CardTitle>
      <CardBody>
        <Alert
          variant="info"
          title="Backend Integration Test"
          isInline
          className="prometheus-converter-info"
        >
          This tests the full production pipeline: your Prometheus data will be sent to the backend
          where the <strong>PrometheusInputDataTransformer</strong> will process it, and the NGUI
          agent will generate a chart configuration.
        </Alert>
        <FormGroup label="Title">
          <input
            type="text"
            value={title}
            onChange={(e) => setTitle(e.target.value)}
            placeholder="Chart Title"
            style={{ 
              width: '100%', 
              padding: '8px', 
              border: '1px solid #ccc', 
              borderRadius: '4px' 
            }}
          />
        </FormGroup>

        <FormGroup label="Chart Type">
          <FormSelect
            value={chartType}
            onChange={(_event, value) => setChartType(value as 'line' | 'bar')}
          >
            <FormSelectOption value="line" label="Line" />
            <FormSelectOption value="bar" label="Bar" />
          </FormSelect>
        </FormGroup>

        <FormGroup label="Downsample (take every Nth point)">
          <input
            type="number"
            value={downsample}
            onChange={(e) => setDownsample(e.target.value)}
            min="1"
            style={{ 
              width: '100%', 
              padding: '8px', 
              border: '1px solid #ccc', 
              borderRadius: '4px' 
            }}
          />
        </FormGroup>

        <FormGroup label="Prometheus Response JSON">
          <div style={{ marginBottom: '8px', fontSize: '13px', color: '#6a6e73' }}>
            {prometheusData ? (
              <span>✓ Data loaded ({prometheusData.length} characters)</span>
            ) : (
              <span>⚠️ No data - click "Load Example" or paste your Prometheus JSON</span>
            )}
          </div>
          <TextArea
            value={prometheusData}
            onChange={(_event, value) => setPrometheusData(value)}
            placeholder="Click 'Load Example' below or paste your Prometheus query_range response JSON here..."
            rows={15}
            style={{ fontFamily: 'monospace', fontSize: '12px' }}
          />
        </FormGroup>

        {error && (
          <Alert variant="danger" title="Error" isInline>
            {error}
          </Alert>
        )}

        <div style={{ display: 'flex', gap: '8px', marginTop: '12px' }}>
          <Button variant="primary" onClick={handleConvert}>
            Convert & Send to Chat
          </Button>
          <Button 
            variant="secondary" 
            onClick={() => setPrometheusData(exampleData)}
          >
            Load Example
          </Button>
          <Button 
            variant="link" 
            onClick={() => {
              setPrometheusData('');
              setError(null);
            }}
          >
            Clear
          </Button>
        </div>

        <Alert 
          variant="info" 
          title="How to use" 
          isInline 
          style={{ marginTop: '16px' }}
        >
          <p style={{ fontSize: '12px', margin: '4px 0' }}>
            1. Paste the JSON response from your Prometheus API (the "result" object)
            <br />
            2. Adjust chart settings as needed
            <br />
            3. Click "Convert & Send to Chat" to render it
          </p>
        </Alert>
      </CardBody>
    </Card>
  );
};

