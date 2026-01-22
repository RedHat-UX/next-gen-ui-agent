import type { ComponentHandlerRegistry } from '@rhngui/patternfly-react-renderer';
import { CpuIcon, MemoryIcon } from "@patternfly/react-icons";

// Type for cell formatter values - matches ComponentHandlerRegistry's CellFormatter type
export type CellValue = string | number | boolean | (string | number)[] | null;

/**
 * Registers generic formatters that can be used across multiple data types.
 * These are fallback formatters that don't have data-type specific prefixes.
 */
export function registerGenericFormatters(registry: ComponentHandlerRegistry): string[] {
  const registeredIds: string[] = [];

  // Generic status formatter
  registry.registerFormatter('status', (value: CellValue) => {
    let statusText: string;
    if (typeof value === 'boolean') {
      statusText = value ? 'Active' : 'Inactive';
    } else if (typeof value === 'string') {
      statusText = value;
    } else {
      statusText = 'Unknown';
    }
    return <strong>{statusText}</strong>;
  });
  registeredIds.push('status');

  // Generic price formatter
  registry.registerFormatter('price', (value: CellValue) => {
    let numValue: number;
    if (typeof value === 'number') {
      numValue = value;
    } else if (typeof value === 'string') {
      numValue = parseFloat(value);
      if (isNaN(numValue)) {
        return String(value);
      }
    } else {
      return '-';
    }
    return `$${numValue.toFixed(2)}`;
  });
  registeredIds.push('price');

  // Generic date formatter
  registry.registerFormatter('date', (value: CellValue) => {
    if (typeof value !== 'string') {
      return String(value ?? '');
    }
    try {
      const date = new Date(value);
      return date.toLocaleString();
    } catch {
      return value;
    }
  });
  registeredIds.push('date');

  // Generic name formatter
  registry.registerFormatter('name', (value: CellValue) => {
    const strValue = String(value ?? '');
    return <strong>{strValue}</strong>;
  });
  registeredIds.push('name');

  // Generic namespace formatter
  registry.registerFormatter('namespace', (value: CellValue) => {
    const strValue = String(value ?? '');
    return (
      <span style={{ fontWeight: 'bold', color: 'var(--pf-v5-global--info-color--100)' }}>
        {strValue.toUpperCase()}
      </span>
    );
  });
  registeredIds.push('namespace');

  // Generic CPU usage formatter - with color coding and icon
  const cpuUsageFormatter = (value: CellValue) => {
    // Handle both number and string representations of numbers
    let numValue: number;
    if (typeof value === 'number') {
      numValue = value;
    } else if (typeof value === 'string') {
      numValue = parseFloat(value);
      if (isNaN(numValue)) {
        return String(value ?? '');
      }
    } else {
      return String(value ?? '');
    }
    
    const percentage = (numValue * 100).toFixed(1);
    const color = numValue > 0.3 ? 'var(--pf-v5-global--danger-color--100)' : 
                  numValue > 0.15 ? 'var(--pf-v5-global--warning-color--100)' : 
                  'var(--pf-v5-global--success-color--100)';
    return (
      <span style={{ display: 'flex', alignItems: 'center', gap: '6px' }}>
        <CpuIcon style={{ color }} />
        <strong>{percentage}%</strong>
      </span>
    );
  };
  registry.registerFormatter('cpu_usage', cpuUsageFormatter);
  registeredIds.push('cpu_usage');
  console.log('[Formatters] Registered generic cpu_usage formatter');

  // Generic memory usage formatter - with color coding and icon
  const memoryUsageFormatter = (value: CellValue) => {
    // Handle both number and string representations of numbers
    let numValue: number;
    if (typeof value === 'number') {
      numValue = value;
    } else if (typeof value === 'string') {
      numValue = parseFloat(value);
      if (isNaN(numValue)) {
        return String(value ?? '');
      }
    } else {
      return String(value ?? '');
    }
    
    const percentage = (numValue * 100).toFixed(1);
    const color = numValue > 0.4 ? 'var(--pf-v5-global--danger-color--100)' : 
                  numValue > 0.25 ? 'var(--pf-v5-global--warning-color--100)' : 
                  'var(--pf-v5-global--success-color--100)';
    return (
      <span style={{ display: 'flex', alignItems: 'center', gap: '6px' }}>
        <MemoryIcon style={{ color }} />
        <strong>{percentage}%</strong>
      </span>
    );
  };
  registry.registerFormatter('memory_usage', memoryUsageFormatter);
  registeredIds.push('memory_usage');
  console.log('[Formatters] Registered generic memory_usage formatter');

  // Generic URL formatter - renders URLs as clickable links
  registry.registerFormatter('url', (value: CellValue) => {
    const strValue = String(value ?? '');
    if (!strValue || (!strValue.startsWith('http://') && !strValue.startsWith('https://'))) {
      return strValue;
    }
    return (
      <a 
        href={strValue} 
        target="_blank" 
        rel="noopener noreferrer"
        style={{ 
          color: 'var(--pf-v5-global--link--Color)',
          textDecoration: 'underline',
          cursor: 'pointer'
        }}
      >
        {strValue}
      </a>
    );
  });
  registeredIds.push('url');
  console.log('[Formatters] Registered generic url formatter');

  return registeredIds;
}

