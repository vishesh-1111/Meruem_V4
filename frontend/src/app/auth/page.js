"use client";

import { Button } from "@/components/ui/button";
import {
  Card,
  CardDescription,
  CardFooter,
  CardHeader,
  CardTitle,
} from "@/components/ui/card";

import Image from "next/image";
import Link from "next/link";
import { useState } from "react";

export default function CardDemo() {
  const [isLoading, setIsLoading] = useState(false);

  const handleGoogleLogin = async () => {
    try {
      setIsLoading(true);
      
      const response = await fetch(`${process.env.NEXT_PUBLIC_API_BASE_URL}/auth/google`, {
        method: "GET",
        headers: {
          "Content-Type": "application/json",
        },
      });

      if (!response.ok) {
        throw new Error("Failed to get authorization URL");
      }

      const data = await response.json();
      console.log(data)
      
      // Redirect to the Google OAuth URL
      if (data.url) {
        // Don't reset loading state - keep button disabled until redirect
        window.location.href = data.url;
        // The page will redirect, so this code won't continue
        return;
      } else {
        console.error("No authorization URL received");
        setIsLoading(false); // Only reset if no redirect
      }
    } catch (error) {
      console.error("Error during Google login:", error);
      setIsLoading(false); // Only reset on error
    }
  };
  return (
    <div className="flex items-center justify-center min-h-screen bg-gray-50">
      <Card className="w-full max-w-sm rounded-2xl shadow-lg">
        {/* Header */}
        <CardHeader className="flex flex-col items-center gap-6 py-10">
          <div className="w-28 h-28 rounded-full overflow-hidden flex items-center justify-center">
            <Image
              src="/images/komugi.jpg"
              alt="Logo"
              width={112}
              height={112}
              className="object-contain"
            />
          </div>
          <CardTitle className="text-center text-2xl font-bold text-gray-900">
            Welcome to Meruem
          </CardTitle>
          <CardDescription className="text-center text-gray-500">
            Login or signup to your account
          </CardDescription>
        </CardHeader>

        {/* Footer */}
        <CardFooter className="flex flex-col gap-4">
          <Button 
            variant="outline" 
            className="w-full" 
            onClick={handleGoogleLogin}
            disabled={isLoading}
          >
            {isLoading ? "Loading..." : "Continue with Google"}
          </Button>
          <div className="text-center text-sm text-gray-600">
            Read our{" "}
            <Link href="/privacy" className="underline">
              Privacy Policy
            </Link>{" "}
            and{" "}
            <Link href="/terms" className="underline">
              Terms of Service
            </Link>
          </div>
        </CardFooter>
      </Card>
    </div>
  );
}
