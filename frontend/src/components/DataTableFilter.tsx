import React, { useState, useCallback } from 'react';
import {
  Box,
  Paper,
  TextField,
  InputAdornment,
  Button,
  Menu,
  MenuItem,
  Chip,
  Stack,
} from '@mui/material';
import SearchIcon from '@mui/icons-material/Search';
import FilterListIcon from '@mui/icons-material/FilterList';
import GetAppIcon from '@mui/icons-material/GetApp';

export interface FilterOption {
  key: string;
  label: string;
  type: 'text' | 'select' | 'date' | 'checkbox';
  options?: Array<{ label: string; value: string | number }>;
}

interface DataTableFilterProps {
  onSearch?: (query: string) => void;
  onFilter?: (filters: Record<string, unknown>) => void;
  onExport?: () => void;
  filterOptions?: FilterOption[];
  showSearch?: boolean;
  showFilter?: boolean;
  showExport?: boolean;
}

export const DataTableFilter: React.FC<DataTableFilterProps> = ({
  onSearch,
  onFilter,
  onExport,
  filterOptions = [],
  showSearch = true,
  showFilter = true,
  showExport = true,
}) => {
  const [searchQuery, setSearchQuery] = useState('');
  const [filterAnchor, setFilterAnchor] = useState<null | HTMLElement>(null);
  const [activeFilters, setActiveFilters] = useState<Record<string, unknown>>({});

  const handleSearch = useCallback(
    (value: string) => {
      setSearchQuery(value);
      onSearch?.(value);
    },
    [onSearch]
  );

  const handleFilterOpen = (event: React.MouseEvent<HTMLButtonElement>) => {
    setFilterAnchor(event.currentTarget);
  };

  const handleFilterClose = () => {
    setFilterAnchor(null);
  };

  const handleFilterChange = (key: string, value: unknown) => {
    const newFilters = { ...activeFilters, [key]: value };
    setActiveFilters(newFilters);
    onFilter?.(newFilters);
  };

  const handleClearFilter = (key: string) => {
    const newFilters = { ...activeFilters };
    delete newFilters[key];
    setActiveFilters(newFilters);
    onFilter?.(newFilters);
  };

  return (
    <Paper sx={{ p: 2 }}>
      <Stack spacing={2}>
        <Box display="flex" gap={1} alignItems="center" flexWrap="wrap">
          {showSearch && (
            <TextField
              size="small"
              placeholder="Search..."
              value={searchQuery}
              onChange={(e) => handleSearch(e.target.value)}
              InputProps={{
                startAdornment: (
                  <InputAdornment position="start">
                    <SearchIcon />
                  </InputAdornment>
                ),
              }}
              sx={{ minWidth: 250 }}
            />
          )}

          {showFilter && filterOptions.length > 0 && (
            <>
              <Button
                variant="outlined"
                size="small"
                startIcon={<FilterListIcon />}
                onClick={handleFilterOpen}
              >
                Filters
              </Button>
              <Menu
                anchorEl={filterAnchor}
                open={Boolean(filterAnchor)}
                onClose={handleFilterClose}
              >
                {filterOptions.map((option) => (
                  <MenuItem key={option.key}>
                    {option.type === 'select' && option.options && (
                      <TextField
                        select
                        size="small"
                        label={option.label}
                        value={activeFilters[option.key] || ''}
                        onChange={(e) => handleFilterChange(option.key, e.target.value)}
                      >
                        <MenuItem value="">All</MenuItem>
                        {option.options.map((opt) => (
                          <MenuItem key={opt.value} value={opt.value}>
                            {opt.label}
                          </MenuItem>
                        ))}
                      </TextField>
                    )}
                  </MenuItem>
                ))}
              </Menu>
            </>
          )}

          {showExport && (
            <Button
              variant="outlined"
              size="small"
              startIcon={<GetAppIcon />}
              onClick={onExport}
            >
              Export CSV
            </Button>
          )}
        </Box>

        {Object.keys(activeFilters).length > 0 && (
          <Box display="flex" gap={1} flexWrap="wrap">
            {Object.entries(activeFilters).map(([key, value]) => (
              <Chip
                key={key}
                label={`${key}: ${value}`}
                onDelete={() => handleClearFilter(key)}
                size="small"
              />
            ))}
          </Box>
        )}
      </Stack>
    </Paper>
  );
};
