"use client"; // mark this as a client component

import React, { useEffect, useState } from "react";
import { useSearchParams, useRouter } from "next/navigation";

export default function OAuthCallback() {
  const searchParams = useSearchParams();
  const router = useRouter();
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const codeParam = searchParams.get("code");

    if (!codeParam) {
      setError("Code not provided");
      return;
    }

    const code = decodeURIComponent(codeParam);

    // Call the FastAPI backend
    fetch(`${process.env.NEXT_PUBLIC_API_BASE_URL}/auth/google/callback`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ code }),
      credentials: "include", // include cookies
    })
      .then((res) => {
        if (!res.ok) throw new Error("Failed to authenticate");
        return res.json();
      })
      .then(() => {
        router.push("/"); // redirect on success
      })
      .catch((err) => {
        console.error(err);
        setError("Authentication failed");
      });
  }, [searchParams, router]);

  if (error) return <p>{error}</p>;

  return <p>Authenticating...</p>;
}




