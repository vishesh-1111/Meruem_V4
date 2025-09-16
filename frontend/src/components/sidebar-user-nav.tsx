'use client';

import { ChevronUp } from 'lucide-react';
import Image from 'next/image';
import type { User } from '@/lib/types'
// import { signOut, useSession } from 'next-auth/react';
import { useTheme } from 'next-themes';
import { WorkspaceDrawer } from './workspace-drawer';
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
import { useRouter } from 'next/navigation';
// import { toast } from './toast';
// import { LoaderIcon } from './icons';
// import { guestRegex } from '@/lib/constants';

export function SidebarUserNav({ user }: { user: User }) {
  console.log("User in SidebarUserNav:", user.profile_url);
  const router = useRouter();
  // const { data, status } = useSession();
  const { setTheme, resolvedTheme } = useTheme();

  // const isGuest = guestRegex.test(data?.user?.email ?? '');

  return (
    <SidebarMenu>
      <SidebarMenuItem>
        <DropdownMenu>
          <DropdownMenuTrigger asChild>
            
              <SidebarMenuButton
                data-testid="user-nav-button"
                className="data-[state=open]:bg-sidebar-accent bg-background data-[state=open]:text-sidebar-accent-foreground h-10"
              >
                <Image
                  src={user.profile_url}
                  alt={user.email ?? 'User Avatar'}
                  width={24}
                  height={24}
                  className="rounded-full"
                  referrerPolicy='no-referrer'
                />
                 <span data-testid="user-email" className="truncate">
                  {user?.email}
                </span>

                {/* {user.email} */}
            
                <ChevronUp className="ml-auto" />
              </SidebarMenuButton>
            
          </DropdownMenuTrigger>
          <DropdownMenuContent
            data-testid="user-nav-menu"
            side="top"
            className="w-[--radix-popper-anchor-width]"
          >
            <DropdownMenuItem
              data-testid="user-nav-item-theme"
              className="cursor-pointer"
              onSelect={() => setTheme(resolvedTheme === 'dark' ? 'light' : 'dark')}
            >
               {/* {user.profile_url} */}
              {`Toggle ${resolvedTheme === 'light' ? 'dark' : 'light'} mode`}
            </DropdownMenuItem>
            <DropdownMenuSeparator />
            <DropdownMenuItem asChild data-testid="user-nav-item-auth">
              <button
                type="button"
                className="w-full cursor-pointer"
                onClick={() => {
                  router.push('http://localhost:80/auth/logout');
                  }
                }
              >
                Sign out
              </button>
            </DropdownMenuItem>
          </DropdownMenuContent>
        </DropdownMenu>
      </SidebarMenuItem>
    </SidebarMenu>
  );
}
