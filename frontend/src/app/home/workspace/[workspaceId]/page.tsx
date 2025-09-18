import { cookies } from 'next/headers';
import { notFound, redirect } from 'next/navigation';
// import { auth } from '@/app/(auth)/auth';

// import { Chat } from '@/components/chat';
// import { getChatById, getMessagesByChatId } from '@/lib/db/queries';
// import { DataStreamHandler } from '@/components/data-stream-handler';
// import { DEFAULT_CHAT_MODEL } from '@/lib/ai/models';
// import { convertToUIMessages } from '@/lib/utils';
// import { ChatHeader } from "@/components/chat-header";
export default async function Page(props: { params: Promise<{ workspaceId: string }> }) {

  const params = await props.params;
  const { workspaceId } = params;
  const cookieStore = await cookies()
  const token = cookieStore.get('meruem_access_token')?.value;


    const connections = await fetch(`http://localhost:80/connections/workspace/${workspaceId}`,
      {
      headers: {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${token}`,
      },
    }
    ).then((res) => res.json())
  

//   if (!chat) {
//     notFound();
//   }

//   const session = await auth();

//   if (!session) {
//     redirect('/api/auth/guest');
//   }

//   if (chat.visibility === 'private') {
//     if (!session.user) {
//       return notFound();
//     }

//     if (session.user.id !== chat.userId) {
//       return notFound();
//     }
//   }

  // const messagesFromDb = await getMessagesByChatId({
  //   id,
  // });

  // const uiMessages = convertToUIMessages(messagesFromDb);

  // const cookieStore = await cookies();
  // const chatModelFromCookie = cookieStore.get('chat-model');

  // if (!chatModelFromCookie) {
  //   return (
  //     <>
  //       {/* <Chat
  //         id={chat.id}
  //         initialMessages={uiMessages}
  //         initialChatModel={DEFAULT_CHAT_MODEL}
  //         // initialVisibilityType={chat.visibility}
  //         // isReadonly={session?.user?.id !== chat.userId}
  //         // isReadonly={true}
  //         // session={session}
  //         autoResume={true}
  //         // initialLastContext={chat.lastContext ?? undefined}
  //       />
  //       <DataStreamHandler /> */}
  //     </>
  //   );
  // }

  return (
    <>
        {JSON.stringify(connections)}
    </>
  );
}



// export default function Page() {  
//   console.log('rendering workspace chat ui')
//   return(       

//      <Chat
//         id={"132222222222222222222222222222223232"}
//         initialMessages={[]}
//         initialChatModel={DEFAULT_CHAT_MODEL}
//         // initialVisibilityType={chat.visibility}
//         // isReadonly={session?.user?.id !== chat.userId}
//         // session={session}
//         autoResume={true}
//         // initialLastContext={chat.lastContext ?? undefined}
//       />
//     // <></>
  
//   );
// }