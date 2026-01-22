import type { ComponentHandlerRegistry } from '@rhngui/patternfly-react-renderer';
import { Label } from "@patternfly/react-core";
import { 
  CheckCircleIcon, 
  TimesCircleIcon, 
  DollarSignIcon,
  ShoppingCartIcon,
  ExclamationCircleIcon,
  ClockIcon
} from "@patternfly/react-icons";
import { registerGenericFormatters, type CellValue } from './genericFormatters';
import { registerRowClickHandlers } from '../handlers/rowClickHandlers';

/**
 * Registers formatters specific to the "products" data type.
 */
function registerProductsFormatters(registry: ComponentHandlerRegistry): string[] {
  const registeredIds: string[] = [];

  const statusFormatter = (value: CellValue) => {
    let boolValue: boolean;
    if (typeof value === 'boolean') {
      boolValue = value;
    } else if (typeof value === 'string') {
      const lowerValue = value.toLowerCase();
      boolValue = lowerValue === 'true' || lowerValue === 'active' || lowerValue === 'in stock';
    } else {
      boolValue = false;
    }
    
    return boolValue ? (
      <Label color="green" icon={<CheckCircleIcon />}>
        In Stock
      </Label>
    ) : (
      <Label color="red" icon={<TimesCircleIcon />}>
        Out of Stock
      </Label>
    );
  };
  
  registry.registerFormatter('products.status', statusFormatter);
  registeredIds.push('products.status');

  registry.registerFormatter('products.price', (value: CellValue) => {
    let numValue: number;
    if (typeof value === 'number') {
      numValue = value;
    } else if (typeof value === 'string') {
      numValue = parseFloat(value);
      if (isNaN(numValue)) {
        return <span>{String(value)}</span>;
      }
    } else {
      return <span>-</span>;
    }
    
    return (
      <span style={{ display: 'flex', alignItems: 'center', gap: '6px' }}>
        <DollarSignIcon style={{ color: '#0066cc' }} />
        <strong>{numValue.toFixed(2)}</strong>
      </span>
    );
  });
  registeredIds.push('products.price');

  registry.registerFormatter('products.name', (value: CellValue) => {
    const strValue = String(value ?? '');
    return (
      <span style={{ display: 'flex', alignItems: 'center', gap: '6px' }}>
        <ShoppingCartIcon style={{ color: '#6a6e73' }} />
        {strValue}
      </span>
    );
  });
  registeredIds.push('products.name');

  return registeredIds;
}

/**
 * Registers formatters specific to the "get_openshift_pods" data type.
 */
function registerOpenShiftPodsFormatters(registry: ComponentHandlerRegistry): string[] {
  const registeredIds: string[] = [];

  // Pod status formatter
  registry.registerFormatter('get_openshift_pods.status', (value: CellValue) => {
    const strValue = String(value ?? '');
    let color: "green" | "orange" | "red" | "blue" = "blue";
    let icon = null;
    switch (strValue.toLowerCase()) {
      case 'running':
        color = 'green';
        icon = <CheckCircleIcon />;
        break;
      case 'pending':
        color = 'orange';
        icon = <ClockIcon />;
        break;
      case 'error':
      case 'failed':
        color = 'red';
        icon = <ExclamationCircleIcon />;
        break;
      default:
        break;
    }
    return <Label color={color} icon={icon}>{strValue}</Label>;
  });
  registeredIds.push('get_openshift_pods.status');

  console.log('[Formatters] Registered OpenShift Pods formatters');
  return registeredIds;
}

/**
 * Registers formatters specific to the "get_openshift_nodes" data type.
 */
function registerOpenShiftNodesFormatters(registry: ComponentHandlerRegistry): string[] {
  const registeredIds: string[] = [];

  // Node status formatter
  registry.registerFormatter('get_openshift_nodes.node_status', (value: CellValue) => {
    const strValue = String(value ?? '');
    const isReady = strValue.toLowerCase() === 'ready';
    return isReady ? (
      <Label color="green" icon={<CheckCircleIcon />}>{strValue}</Label>
    ) : (
      <Label color="red" icon={<ExclamationCircleIcon />}>{strValue}</Label>
    );
  });
  registeredIds.push('get_openshift_nodes.node_status');

  // Version label formatter
  registry.registerFormatter('get_openshift_nodes.version_label', (value: CellValue) => {
    const strValue = String(value ?? '');
    return (
      <code style={{ 
        fontSize: '0.8em', 
        backgroundColor: '#f0f0f0', 
        padding: '2px 4px', 
        borderRadius: '4px' 
      }}>
        {strValue}
      </code>
    );
  });
  registeredIds.push('get_openshift_nodes.version_label');

  console.log('[Formatters] Registered OpenShift Nodes formatters');
  return registeredIds;
}

/**
 * Registers formatters specific to the "pod_data" data type (used for direct InputData).
 * Uses a visually distinct style to differentiate from get_openshift_pods formatters.
 */
function registerPodDataFormatters(registry: ComponentHandlerRegistry): string[] {
  const registeredIds: string[] = [];

  // Pod status formatter - visually distinct with outlined style and different colors
  registry.registerFormatter('pod_data.status', (value: CellValue) => {
    const strValue = String(value ?? '');
    let color: "green" | "orange" | "red" | "blue" | "purple" = "blue";
    let icon = null;
    let variant: "filled" | "outline" = "outline";
    
    switch (strValue.toLowerCase()) {
      case 'running':
        color = 'green';
        variant = 'outline';
        icon = <CheckCircleIcon />;
        break;
      case 'pending':
        color = 'orange';
        variant = 'outline';
        icon = <ClockIcon />;
        break;
      case 'error':
      case 'failed':
        color = 'red';
        variant = 'outline';
        icon = <ExclamationCircleIcon />;
        break;
      default:
        color = 'purple';
        variant = 'outline';
        break;
    }
    
    return (
      <Label 
        color={color} 
        icon={icon}
        variant={variant}
        style={{ 
          fontWeight: 'bold',
          borderWidth: '2px',
          textTransform: 'uppercase',
          fontSize: '0.85em'
        }}
      >
        {strValue}
      </Label>
    );
  });
  registeredIds.push('pod_data.status');

  console.log('[Formatters] Registered pod_data formatters');
  return registeredIds;
}

/**
 * Registers formatters specific to the "cluster_info" data type.
 */
function registerClusterInfoFormatters(registry: ComponentHandlerRegistry): string[] {
  const registeredIds: string[] = [];

  // Cluster status formatter - nice styling for cluster health status
  registry.registerFormatter('cluster_info.status', (value: CellValue) => {
    const strValue = String(value ?? '').toLowerCase();
    let color: "green" | "orange" | "red" | "blue" = "blue";
    let icon = null;
    
    switch (strValue) {
      case 'healthy':
        color = 'green';
        icon = <CheckCircleIcon />;
        break;
      case 'degraded':
      case 'warning':
        color = 'orange';
        icon = <ExclamationCircleIcon />;
        break;
      case 'unhealthy':
      case 'error':
      case 'failed':
        color = 'red';
        icon = <TimesCircleIcon />;
        break;
      default:
        color = 'blue';
        break;
    }
    
    return (
      <Label 
        color={color} 
        icon={icon}
        style={{ 
          fontWeight: 'bold',
          textTransform: 'capitalize',
          fontSize: '0.9em'
        }}
      >
        {String(value ?? '')}
      </Label>
    );
  });
  registeredIds.push('cluster_info.status');

  console.log('[Formatters] Registered cluster_info formatters');
  return registeredIds;
}

/**
 * Registers all formatters for the NGUI E2E client.
 * This includes data-type specific formatters and generic fallback formatters.
 * 
 * @param registry - The ComponentHandlerRegistry instance to register formatters with
 * @returns A cleanup function to unregister all formatters
 */
export function registerFormatters(registry: ComponentHandlerRegistry): () => void {
  console.log('[Formatters] Registering all formatters and handlers...');
  
  // Register all formatter categories and collect their IDs
  const allRegisteredIds: string[] = [
    ...registerGenericFormatters(registry),
    ...registerProductsFormatters(registry),
    ...registerOpenShiftPodsFormatters(registry),
    ...registerOpenShiftNodesFormatters(registry),
    ...registerPodDataFormatters(registry),
    ...registerClusterInfoFormatters(registry),
  ];

  // Register row click handlers
  const handlerIds = registerRowClickHandlers(registry);
  allRegisteredIds.push(...handlerIds);

  console.log(`[Formatters] Registered ${allRegisteredIds.length} formatters and handlers`);

  // Return cleanup function to unregister all formatters
  return () => {
    allRegisteredIds.forEach(id => {
      registry.unregisterFormatter(id);
    });
    console.log('[Formatters] Unregistered all formatters');
  };
}
