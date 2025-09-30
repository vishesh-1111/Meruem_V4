import { NextRequest, NextResponse } from 'next/server';
import { cookies } from 'next/headers';

export async function GET(request: NextRequest) {
  try {
    const { searchParams } = new URL(request.url);
    const codeParam = searchParams.get('code');

    if (!codeParam) {
      return NextResponse.json({ error: 'Code not provided' }, { status: 400 });
    }

    const code = decodeURIComponent(codeParam);

    // Call the FastAPI backend
    const response = await fetch(`${process.env.NEXT_PUBLIC_API_BASE_URL}/auth/google/callback`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ code }),
    });

    if (!response.ok) {
      throw new Error('Failed to authenticate with backend');
    }

    const data = await response.json();
    const accessToken = data.meruem_access_token;

    if (!accessToken) {
      throw new Error('Access token not received from backend');
    }

    // Set cookie with the access token
    const cookieStore = await cookies();
    cookieStore.set('meruem_access_token', accessToken, {
      httpOnly: true,
      secure: true,
      sameSite: 'none',
      maxAge: 30 * 60, 
      path: '/',
    });

    // Redirect to home page
    return NextResponse.redirect(new URL('/', request.url));
  } catch (error) {
    console.error('OAuth callback error:', error);
    return NextResponse.json(
      { error: 'Authentication failed' }, 
      { status: 500 }
    );
  }
}

