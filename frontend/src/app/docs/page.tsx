
import { Book } from 'lucide-react';

export default function DocsPage() {
  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-50 via-blue-50 to-indigo-50 dark:from-slate-900 dark:via-slate-800 dark:to-indigo-900 relative overflow-hidden">
      {/* Background Elements */}
      <div className="absolute inset-0 overflow-hidden">
        <div className="absolute -top-1/2 -left-1/2 w-full h-full bg-gradient-to-r from-blue-400/20 to-purple-400/20 rounded-full blur-3xl"></div>
        <div className="absolute -bottom-1/2 -right-1/2 w-full h-full bg-gradient-to-r from-purple-400/20 to-pink-400/20 rounded-full blur-3xl"></div>
      </div>

      {/* Main Content */}
      <div className="relative z-10 flex flex-col items-center justify-center min-h-screen px-4 sm:px-6 lg:px-8">
        <div className="max-w-2xl mx-auto text-center">
          
          {/* Logo/Icon */}
          <div className="mb-8">
            <div className="inline-flex items-center justify-center w-20 h-20 bg-gradient-to-r from-blue-500 to-purple-600 rounded-full shadow-2xl">
              <Book className="w-10 h-10 text-white" />
            </div>
          </div>

          {/* Main Heading */}
          <div className="mb-6">
            <h1 className="text-5xl sm:text-6xl lg:text-7xl font-bold bg-gradient-to-r from-blue-600 via-purple-600 to-indigo-600 bg-clip-text text-transparent mb-4">
              Documentation
            </h1>
            <div className="flex items-center justify-center gap-2 mb-4">
              <span className="text-2xl sm:text-3xl font-semibold text-slate-700 dark:text-slate-300">
                Coming Soon
              </span>
            </div>
          </div>

          {/* Simple Description */}
          <p className="text-lg sm:text-xl text-slate-600 dark:text-slate-400 mb-8 max-w-xl mx-auto leading-relaxed">
            Comprehensive documentation for <span className="font-semibold text-blue-600 dark:text-blue-400">Meruem </span> is currently in development.
          </p>
        </div>
      </div>
    </div>
  );
}
