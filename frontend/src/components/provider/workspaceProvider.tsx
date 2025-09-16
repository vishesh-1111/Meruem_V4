'use client';

import React, { createContext, useContext, useMemo, useState } from 'react';

// Define the Workspace type
export type Workspace = {
  id: string;
  name: string;
};

// Define the context value interface
interface WorkspaceContextValue {
  workspaces: Workspace[];
  setWorkspaces: React.Dispatch<React.SetStateAction<Workspace[]>>;
}

// Create the context
const WorkspaceContext = createContext<WorkspaceContextValue | null>(null);

// Provider component
export function WorkspaceContextProvider({
  children,
  initialWorkspaces = [],
}: {
  children: React.ReactNode;
  initialWorkspaces?: Workspace[];
}) {
  const [workspaces, setWorkspaces] = useState<Workspace[]>(initialWorkspaces);

  const value = useMemo(
    () => ({ workspaces, setWorkspaces }),
    [workspaces]
  );

  return (
    <WorkspaceContext.Provider value={value}>
      {children}
    </WorkspaceContext.Provider>
  );
}

// Hook for consuming the context
export function useWorkspaces() {
  const context = useContext(WorkspaceContext);
  if (!context) {
    throw new Error('useWorkspaces must be used within a WorkspaceContextProvider');
  }
  return context;
}
