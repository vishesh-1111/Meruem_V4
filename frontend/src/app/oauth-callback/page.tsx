// app/oauth-callback/page.tsx
import { Suspense } from "react";
import OAuthCallbackHandler from "./OAuthCallbackHandler";

export default function OAuthCallbackPage() {
  return (
    <Suspense fallback={<div>Loading authentication...</div>}>
      <OAuthCallbackHandler />
    </Suspense>
  );
}
