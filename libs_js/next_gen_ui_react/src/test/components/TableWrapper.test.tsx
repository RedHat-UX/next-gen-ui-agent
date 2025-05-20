import { render, fireEvent, screen } from "@testing-library/react";
import { vi } from "vitest";

import TableWrapper from "../../components/TableWrapper";

const columns = [
  { key: "name", label: "Name" },
  { key: "age", label: "Age" },
];

const rows = [
  { name: "John Doe", age: 28 },
  { name: "Jane Smith", age: 34 },
];

describe("TableWrapper Component", () => {
  it("should render the table correctly", () => {
    render(<TableWrapper columns={columns} rows={rows} caption="User Table" variant={undefined} graph={undefined} onRowSelect={undefined} actions={undefined} setCustomData={undefined} />);
    expect(screen.getByText("User Table")).toBeInTheDocument();
    expect(screen.getByText("Name")).toBeInTheDocument();
    expect(screen.getByText("Age")).toBeInTheDocument();
  });

  it("should render the table with selectable rows", () => {
    render(
      <TableWrapper
        columns={columns}
        rows={rows}
        caption="User Table"
        selectable={true} variant={undefined} graph={undefined} onRowSelect={undefined} actions={undefined} setCustomData={undefined}      />
    );
    const checkboxes = screen.getAllByRole("checkbox");
    expect(checkboxes).toHaveLength(3); // 1 for "select all", 2 for individual rows
  });

  it('should select and deselect a row', () => {
    const setCustomDataMock = vi.fn();
    const onRowSelectMock = vi.fn();
  
    const mockColumns = [
      { label: 'Column 1', key: 'test1' },
      { label: 'Column 2', key: 'test2' },
    ];
  
    const mockRows = [
      { id: 1, test1: 'test1', test2: 'test2' },
    ];
  
    const { getByTestId, getByLabelText } = render(
      <TableWrapper
        columns={mockColumns}
        rows={mockRows}
        caption="Test Table"
        selectable={true}
        onRowSelect={onRowSelectMock}
        setCustomData={setCustomDataMock}
      />
    );
  
    const row = getByTestId('row-1');
    const checkbox = getByLabelText('Select row 0');
  
    // Select the row
    fireEvent.click(checkbox);
  
    // After selection, the mock function should be called with the selected row
    expect(setCustomDataMock).toHaveBeenCalledWith([
      {
        id: 1,
        test1: 'test1',
        test2: 'test2',
      },
    ]);
  
    // Deselect the row
    fireEvent.click(checkbox); // Deselect by clicking the checkbox again
  
    // After deselection, the mock function should be called with an empty array
    expect(setCustomDataMock).toHaveBeenCalledWith([]);
  });

  it("should select all rows", () => {
    const mockOnRowSelect = vi.fn();
    const mockSetCustomData = vi.fn();
  
    render(
      <TableWrapper
        columns={columns}
        rows={rows}
        caption="User Table"
        selectable={true}
        onRowSelect={mockOnRowSelect}
        setCustomData={mockSetCustomData}
        variant={undefined}
        graph={undefined}
        actions={undefined}
      />
    );
  
    // Select all rows
    fireEvent.click(screen.getByLabelText("Select all rows"));
    expect(mockOnRowSelect).toHaveBeenCalledWith(rows);
  
    // Deselect all rows
    fireEvent.click(screen.getByLabelText("Select all rows"));
    expect(mockOnRowSelect).toHaveBeenCalledWith([]);
  });
  
  it("should render the chart if graph data is provided", () => {
    const graph = {
      column: "age",
      title: "Age Chart",
    };
    render(
      <TableWrapper
        columns={columns}
        rows={rows}
        caption="User Table"
        graph={graph} variant={undefined} onRowSelect={undefined} actions={undefined} setCustomData={undefined}      />
    );
    expect(screen.getByTitle("Age Chart")).toBeInTheDocument();
  });

  it("should not render the chart if no graph data is provided", () => {
    render(
      <TableWrapper columns={columns} rows={rows} caption="User Table" variant={undefined} graph={undefined} onRowSelect={undefined} actions={undefined} setCustomData={undefined} />
    );
    expect(screen.queryByTitle("Chart")).toBeNull();
  });

  it("should call setCustomData when a row is selected or deselected", () => {
    const mockSetCustomData = vi.fn();
    render(
      <TableWrapper
        columns={columns}
        rows={rows}
        caption="User Table"
        selectable={true}
        setCustomData={mockSetCustomData} variant={undefined} graph={undefined} onRowSelect={undefined} actions={undefined}      />
    );

    // Select first row
    fireEvent.click(screen.getAllByRole("checkbox")[1]);
    expect(mockSetCustomData).toHaveBeenCalledWith([rows[0]]);

    // Deselect first row
    fireEvent.click(screen.getAllByRole("checkbox")[1]);
    expect(mockSetCustomData).toHaveBeenCalledWith([]);
  });

  it("should trigger onRowSelect with correct row data when a row is clicked", () => {
    const mockOnRowSelect = vi.fn();
    const mockSetCustomData = vi.fn();
  
    render(
      <TableWrapper
        columns={columns}
        rows={rows}
        caption="User Table"
        selectable={true}
        onRowSelect={mockOnRowSelect}
        setCustomData={mockSetCustomData}
        variant={undefined}
        graph={undefined}
        actions={undefined}
      />
    );
  
    // Select second row (Jane Smith)
    fireEvent.click(screen.getAllByRole("checkbox")[2]);
    expect(mockOnRowSelect).toHaveBeenCalledWith([rows[1]]);
  });

  it("should show the correct row data in the table", () => {
    render(<TableWrapper columns={columns} rows={rows} caption="User Table" variant={undefined} graph={undefined} onRowSelect={undefined} actions={undefined} setCustomData={undefined} />);
    expect(screen.getByText("John Doe")).toBeInTheDocument();
    expect(screen.getByText("28")).toBeInTheDocument();
    expect(screen.getByText("Jane Smith")).toBeInTheDocument();
    expect(screen.getByText("34")).toBeInTheDocument();
  });
});
