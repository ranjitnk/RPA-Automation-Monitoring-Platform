import { Typography } from '@mui/material';
import { DataGrid } from '@/components/grid/DataGrid';
import type { ColDef } from 'ag-grid-community';

interface QueueRow {
  name: string;
  inQueue: number;
  processing: number;
}

const columnDefs: ColDef<QueueRow>[] = [
  { field: 'name', headerName: 'Queue' },
  { field: 'inQueue', headerName: 'In Queue' },
  { field: 'processing', headerName: 'Processing' },
];

export function QueuesPage() {
  return (
    <>
      <Typography variant="h4" gutterBottom>
        Queue Monitoring
      </Typography>
      <DataGrid rowData={[]} columnDefs={columnDefs} />
    </>
  );
}
