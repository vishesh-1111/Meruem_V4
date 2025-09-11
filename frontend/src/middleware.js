import { NextResponse } from 'next/server'

export function middleware(request) {
  const { pathname } = request.nextUrl
  // console.log(pathname)
  
//   // Get cookies from the request
  const meruemsAccessToken = request.cookies.get('meruem_access_token')

//   // Handle root route: /
  if (pathname === '/') {

    // If no access token, redirect to auth
    if (!meruemsAccessToken) {
      return NextResponse.redirect(new URL('/landing', request.url))
    }
    else{
     return NextResponse.redirect(new URL('/home', request.url))
    }
}

//   if (pathname === '/landing'&&meruemsAccessToken) {

//      return NextResponse.redirect(new URL('/home', request.url))
// }
  
  // For all other routes, continue normally
  return NextResponse.next()
}

export const config = {
  matcher: [
    /*
     * Match all request paths except for the ones starting with:
     * - api (API routes)
     * - _next/static (static files)
     * - _next/image (image optimization files)
     * - favicon.ico (favicon file)
     * - auth (auth pages - to prevent redirect loops)
     */
    '/((?!api|_next/static|_next/image|favicon.ico|auth).*)',
  ],
}