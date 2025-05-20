import {
  Chart,
  ChartBar,
  ChartAxis,
  ChartGroup,
  ChartThemeColor,
} from "@patternfly/react-charts";
import {
  Table,
  Thead,
  Tr,
  Th,
  Tbody,
  Td,
  Caption,
} from "@patternfly/react-table";
import { useState } from "react";

const TableWrapper = ({
  columns,
  rows,
  caption,
  variant,
  graph,
  selectable = false,
  onRowSelect,
  actions,
  setCustomData,
}) => {
  const [selectedRows, setSelectedRows] = useState([]);

  const toggleRow = (index) => {
    const newSelected = selectedRows.includes(index)
      ? selectedRows.filter((i) => i !== index)
      : [...selectedRows, index];
    setSelectedRows(newSelected);

    onRowSelect?.(newSelected.map((i) => rows[i]));
    setCustomData(newSelected.map((i) => rows[i]));
  };

  const toggleAllRows = () => {
    const allSelected = selectedRows.length === rows.length;
    const newSelected = allSelected ? [] : rows.map((_, i) => i);
    setSelectedRows(newSelected);

    onRowSelect?.(newSelected.map((i) => rows[i]));
    setCustomData(newSelected.map((i) => rows[i]));
  };

  const graphData =
    graph && graph.column
      ? rows.map((row) => ({ x: row[columns[0].key], y: row[graph.column] }))
      : [];

  return (
    <div>
      <Table variant={variant} borders={variant !== "compactBorderless"}>
        {caption && (
          <Caption>
            <div
              style={{
                display: "flex",
                justifyContent: "space-between",
                alignItems: "center",
              }}
            >
              <span>{caption}</span>
              {actions}
            </div>
          </Caption>
        )}
        <Thead>
          <Tr>
            {selectable && (
              <Th>
                <input
                  type="checkbox"
                  aria-label="Select all rows"
                  checked={selectedRows.length === rows.length}
                  onChange={toggleAllRows}
                />
              </Th>
            )}
            {columns.map((col, index) => (
              <Th key={index}>{col.label}</Th>
            ))}
          </Tr>
        </Thead>
        <Tbody>
          {rows.map((row, rowIndex) => (
            <Tr key={rowIndex} data-testid={`row-${row.id ?? rowIndex}`} >
              {selectable && (
                <Td>
                  <input
                    type="checkbox"
                    aria-label={`Select row ${rowIndex}`}
                    checked={selectedRows.includes(rowIndex)}
                    onChange={() => toggleRow(rowIndex)}
                  />
                </Td>
              )}
              {columns.map((col, colIndex) => (
                <Td key={colIndex}>{row[col.key]}</Td>
              ))}
            </Tr>
          ))}
        </Tbody>
      </Table>

      {graph && (
        <div style={{ height: "300px" }}>
          <Chart
            ariaTitle={graph.title || "Chart"}
            domainPadding={{ x: [30, 25] }}
            height={300}
            width={600}
            themeColor={ChartThemeColor.multiUnordered}
          >
            <ChartAxis />
            <ChartAxis dependentAxis />
            <ChartGroup>
              <ChartBar data={graphData} barWidth={30} />
            </ChartGroup>
          </Chart>
        </div>
      )}
    </div>
  );
};

export default TableWrapper;
