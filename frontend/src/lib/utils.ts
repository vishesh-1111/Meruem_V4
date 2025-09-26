import type {
  CoreAssistantMessage,
  CoreToolMessage,
  UIMessage,
  UIMessagePart,
} from 'ai';
import { type ClassValue, clsx } from 'clsx';
import { twMerge } from 'tailwind-merge';
// import type { DBMessage, Document } from '@/lib/db/schema';
import { ChatSDKError, type ErrorCode } from './errors';
import type { ChatMessage,  CustomUIDataTypes } from './types';
import { formatISO } from 'date-fns';
import { cache } from 'react';
export function cn(...inputs: ClassValue[]) {
  return twMerge(clsx(inputs));
}

// // Base URL for your backend - you can set this via environment variable
const BASE_URL = process.env.NEXT_PUBLIC_API_BASE_URL || '';

export const fetcher = async (url: string) => {
  // Prepend base URL if the URL is relative
  const fullUrl = url.startsWith('/') ? `${BASE_URL}${url}` : url;
  const response = await fetch(fullUrl,{credentials: 'include'});
  console.log('Fetching from:', fullUrl)

  if (!response.ok) {
    const { code, cause } = await response.json();
    throw new ChatSDKError(code as ErrorCode, cause);
  }

  return response.json();
};

// export async function fetchWithErrorHandlers(
//   input: RequestInfo | URL,
//   init?: RequestInit,
// ) {
//   try {
//     const response = await fetch(input, init);
//     console.log("response",response)

//     if (!response.ok) {
//       const { code, cause } = await response.json();
//       throw new ChatSDKError(code as ErrorCode, cause);
//     }
//         console.log("response",response)

//     return response;
//   } catch (error: unknown) {
//     if (typeof navigator !== 'undefined' && !navigator.onLine) {
//       throw new ChatSDKError('offline:chat');
//     }

//     throw error;
//   }
// }

// export function getLocalStorage(key: string) {
//   if (typeof window !== 'undefined') {
//     return JSON.parse(localStorage.getItem(key) || '[]');
//   }
//   return [];
// }

// export function generateUUID(): string {
//   return 'xxxxxxxx-xxxx-4xxx-yxxx-xxxxxxxxxxxx'.replace(/[xy]/g, (c) => {
//     const r = (Math.random() * 16) | 0;
//     const v = c === 'x' ? r : (r & 0x3) | 0x8;
//     return v.toString(16);
//   });
// }

// type ResponseMessageWithoutId = CoreToolMessage | CoreAssistantMessage;
// type ResponseMessage = ResponseMessageWithoutId & { id: string };

// export function getMostRecentUserMessage(messages: Array<UIMessage>) {
//   const userMessages = messages.filter((message) => message.role === 'user');
//   return userMessages.at(-1);
// }

// // export function getDocumentTimestampByIndex(
// //   documents: Array<Document>,
// //   index: number,
// // ) {
// //   if (!documents) return new Date();
// //   if (index > documents.length) return new Date();

// //   return documents[index].createdAt;
// // }

// export function getTrailingMessageId({
//   messages,
// }: {
//   messages: Array<ResponseMessage>;
// }): string | null {
//   const trailingMessage = messages.at(-1);

//   if (!trailingMessage) return null;

//   return trailingMessage.id;
// }

export function sanitizeText(text: string) {
  return text.replace('<has_function_call>', '');
}

// export function convertToUIMessages(messages: DBMessage[]): ChatMessage[] {
//   return messages.map((message) => ({
//     id: message.id,
//     role: message.role as 'user' | 'assistant' | 'system',
//     parts: message.parts as UIMessagePart<CustomUIDataTypes, ChatTools>[],
//     metadata: {
//       createdAt: formatISO(message.createdAt),
//     },
//   }));
// }

export function getTextFromMessage(message: ChatMessage): string {
  return message.parts
    .filter((part) => part.type === 'text')
    .map((part) => part.text)
    .join('');
}

export const getAlldata = cache(async (token:string) => {
  console.log("fetching cached data hit or miss")
  // This function will only be executed once per render pass
  const res = await fetch(
    `${process.env.NEXT_PUBLIC_API_BASE_URL}/workspace/data`,

    {
      headers: {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${token}`,
      },
    }
  )
   
  return res.json();
});