import { z } from 'zod';
// import type { getWeather } from './ai/tools/get-weather';
// import type { createDocument } from './ai/tools/create-document';
// import type { updateDocument } from './ai/tools/update-document';
// import type { requestSuggestions } from './ai/tools/request-suggestions';
import type { InferUITool, LanguageModelUsage, UIMessage } from 'ai';

// import type { ArtifactKind } from '@/components/artifact';
// import type { Suggestion } from './db/schema';

export type DataPart = { type: 'append-message'; message: string };

export const messageMetadataSchema = z.object({
  createdAt: z.string(),
});

export type MessageMetadata = z.infer<typeof messageMetadataSchema>;

// type weatherTool = InferUITool<typeof getWeather>;
// type createDocumentTool = InferUITool<ReturnType<typeof createDocument>>;
// type updateDocumentTool = InferUITool<ReturnType<typeof updateDocument>>;
// type requestSuggestionsTool = InferUITool<
//   ReturnType<typeof requestSuggestions>
// >;

// export type ChatTools = {
//   getWeather: weatherTool;
//   createDocument: createDocumentTool;
//   updateDocument: updateDocumentTool;
//   requestSuggestions: requestSuggestionsTool;
// };

export type CustomUIDataTypes = {
  textDelta: string;
  imageDelta: string;
  sheetDelta: string;
  codeDelta: string;
  // suggestion: Suggestion;
  appendMessage: string;
  id: string;
  title: string;
  // kind: ArtifactKind;
  clear: null;
  finish: null;
  usage: LanguageModelUsage;
};

export type ChatMessage = UIMessage<
  MessageMetadata,
  CustomUIDataTypes
  // ChatTools
>;

export interface Attachment {
  name: string;
  url: string;
  contentType: string;
}


export type User = {
  id: string; // "68c2b0e15b976448616305a0"
  first_name: string; // "vishesh"
  last_name: string;  // "kumar gautam"
  email: string; // "visheshgautam.official@gmail.com"
  profile_url: string; // "https://lh3.googleusercontent.com/a/..."
};


export type Workspace = {
  id: string; // "68c2b0e15b976448616305a0"
  name: string; // "vishesh workspace"
};


export type Chat = {
  id: string; // "68c2b0e15b976448616305a0"
  name:string; // "vishesh chat"
  createdAt: string; // "2024-06-20T10:20:30Z"
};



export type Connection = {
  id: string; // "68c2b0e15b976448616305a0"
  name:string; // "vishesh chat"
  driver: string; // "mysql"
};