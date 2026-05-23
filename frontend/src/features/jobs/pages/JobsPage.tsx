import { Typography } from '@mui/material';
import { DataGrid } from '@/components/grid/DataGrid';
import type { ColDef } from 'ag-grid-community';

interface JobRow {
  id: number;
  process: string;
  state: string;
  robot: string;
}

const columnDefs: ColDef<JobRow>[] = [
  { field: 'id', headerName: 'Job ID' },
  { field: 'process', headerName: 'Process' },
  { field: 'state', headerName: 'State' },
  { field: 'robot', headerName: 'Robot' },
];

export function JobsPage() {
  return (
    <>
      <Typography variant="h4" gutterBottom>
        Job Monitoring
      </Typography>
      <DataGrid rowData={[]} columnDefs={columnDefs} />
    </>
  );
}
