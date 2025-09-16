import { cookies } from 'next/headers';

import { AppSidebar } from '@/components/app-sidebar';
import { SidebarInset, SidebarProvider } from '@/components/ui/sidebar';
import { WorkspaceContextProvider } from '@/components/provider/workspaceProvider';
// import { auth } from '../(auth)/auth';
import Script from 'next/script';
import { DataStreamProvider } from '@/components/data-stream-provider';

// export const experimental_ppr = true;

export default async function Layout({
  children,
}: {
  children: React.ReactNode;
}) {
  // const [session, cookieStore] = await Promise.all([auth(), cookies()]);
// const user = {
//   id: "68c2b0e15b976448616305a0",
//   first_name: "vishesh",
//   last_name: "kumar gautam",
//   email: "visheshgautam.official@gmail.com",
//   profile_url: "https://picsum.photos/200",
// };
const cookieStore = await cookies();

const token = cookieStore.get('meruem_access_token')?.value;

  const allData = await fetch(
    'http://localhost:80/workspace/data',

    {
       credentials: 'include',
      headers: {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${token}`,
      },
    }
  )
   .then((res) => res.json())

  console.log(allData)

  const isCollapsed = cookieStore.get('sidebar:state')?.value !== 'true';

  return (
    <>
      {/* <Script
        src="https://cdn.jsdelivr.net/pyodide/v0.23.4/full/pyodide.js"
        strategy="beforeInteractive"
      /> */}
    <WorkspaceContextProvider initialWorkspaces={allData.workspaces}>
      <DataStreamProvider>
        <SidebarProvider defaultOpen={!isCollapsed}>
          <AppSidebar user={allData.user} />
          <SidebarInset>{children}</SidebarInset>
        </SidebarProvider>
      </DataStreamProvider>
    </WorkspaceContextProvider>
    </>
  );
}
