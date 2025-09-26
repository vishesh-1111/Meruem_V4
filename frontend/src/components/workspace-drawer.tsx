'use client';

import { ChevronUp, FolderOpen, Plus,ChevronDown } from 'lucide-react';
import { useRouter } from 'next/navigation';
import { useState } from 'react';
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuSeparator,
  DropdownMenuTrigger,
} from '@/components/ui/dropdown-menu';
import {
  SidebarMenu,
  SidebarMenuButton,
  SidebarMenuItem,
} from '@/components/ui/sidebar';
import { useWorkspaces, type Workspace } from '@/components/provider/workspaceProvider';
import {
  Sheet,
  SheetContent,
  SheetHeader,
  SheetTitle,
  SheetTrigger,
} from '@/components/ui/sheet';
import { Button } from '@/components/ui/button';

export function WorkspaceDrawer() {
  const router = useRouter();
  const { workspaces } = useWorkspaces();
  const [activeWorkspace, setActiveWorkspace] = useState<Workspace | null>(
    workspaces.length > 0 ? workspaces[0] : null
  );

  const handleSelectWorkspace = (workspace: Workspace) => {
    setActiveWorkspace(workspace);
    // Navigate to the workspace or update the UI
    router.push(`home/workspace/${workspace.id}`);
  };

  const handleCreateWorkspace = () => {
    // Placeholder for workspace creation flow
    // This could open a modal or navigate to a creation page
    router.push('/home/workspace/new');
  };

  return (
    <SidebarMenu>
      {/* <SidebarMenuItem>
        <DropdownMenu>
          <DropdownMenuTrigger asChild>
            <SidebarMenuButton
              data-testid="workspace-nav-button"
              className="data-[state=open]:bg-sidebar-accent bg-background data-[state=open]:text-sidebar-accent-foreground h-10"
            >
              <FolderOpen className="h-5 w-5" />
              <span data-testid="workspace-name" className="truncate">
                {activeWorkspace?.name || 'Select Workspace'}
              </span>
              <ChevronDown className="ml-auto" />
            </SidebarMenuButton>
          </DropdownMenuTrigger>
          <DropdownMenuContent
            data-testid="workspace-nav-menu"
            side="top"
            className="w-[--radix-popper-anchor-width]"
          >
            {workspaces.map((workspace) => (
              <DropdownMenuItem
                key={workspace.id}
                className="cursor-pointer"
                onSelect={() => handleSelectWorkspace(workspace)}
              >
                {workspace.name}
              </DropdownMenuItem>
            ))}
            {workspaces.length > 0 && <DropdownMenuSeparator />}
            <DropdownMenuItem
              className="cursor-pointer"
              onSelect={handleCreateWorkspace}
            >
              <Plus className="mr-2 h-4 w-4" />
              Create New Workspace
            </DropdownMenuItem>
          </DropdownMenuContent>
        </DropdownMenu>
      </SidebarMenuItem> */}

      {/* Full Workspace List Sheet/Drawer */}
      <SidebarMenuItem>
        <Sheet>
          <SheetTrigger asChild>
            <Button
              variant="ghost"
              size="sm"
              className="w-full justify-start px-2"
              data-testid="workspace-drawer-button"
            >
              <FolderOpen className="mr-2 h-4 w-4" />
              All Workspaces
            </Button>
          </SheetTrigger>
          <SheetContent side="left" className="w-[300px] sm:w-[400px]">
            <SheetHeader>
              <SheetTitle>Your Workspaces</SheetTitle>
            </SheetHeader>
            <div className="py-4">
              {workspaces.length === 0 ? (
                <p className="text-center text-muted-foreground">
                  No workspaces found
                </p>
              ) : (
                <div className="space-y-2">
                  {workspaces.map((workspace) => (
                    <Button
                      key={workspace.id}
                      variant="ghost"
                      size="sm"
                      className={`w-full justify-start ${
                        activeWorkspace?.id === workspace.id
                          ? 'bg-accent'
                          : ''
                      }`}
                      onClick={() => handleSelectWorkspace(workspace)}
                    >
                      <FolderOpen className="mr-2 h-4 w-4" />
                      {workspace.name}
                    </Button>
                  ))}
                </div>
              )}
              <Button
                variant="outline"
                size="sm"
                className="mt-4 w-full"
                onClick={handleCreateWorkspace}
              >
                <Plus className="mr-2 h-4 w-4" />
                Create New Workspace
              </Button>
            </div>
          </SheetContent>
        </Sheet>
      </SidebarMenuItem>
    </SidebarMenu>
  );
}