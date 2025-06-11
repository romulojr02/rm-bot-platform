import { Switch, Route } from "wouter";
import { queryClient } from "./lib/queryClient";
import { QueryClientProvider } from "@tanstack/react-query";
import { Toaster } from "@/components/ui/toaster";
import { TooltipProvider } from "@/components/ui/tooltip";
import { AuthProvider, useAuth } from "@/hooks/use-auth";
import { Landing } from "@/pages/landing";
import { UserDashboard } from "@/pages/user-dashboard";
import { AdminDashboard } from "@/pages/admin-dashboard";

function AppContent() {
  const { user, isLoading } = useAuth();

  if (isLoading) {
    return (
      <div className="min-h-screen bg-slate-700 flex items-center justify-center">
        <div className="text-center">
          <div className="bg-blue-500 p-4 rounded-lg inline-block mb-4">
            <i className="fas fa-robot text-white text-3xl"></i>
          </div>
          <div className="text-white text-xl font-semibold mb-2">RM Bot</div>
          <div className="text-gray-400">Carregando...</div>
        </div>
      </div>
    );
  }

  return (
    <Switch>
      <Route path="/">
        {user ? (
          user.isAdmin ? <AdminDashboard /> : <UserDashboard />
        ) : (
          <Landing />
        )}
      </Route>
      <Route path="/admin">
        {user?.isAdmin ? <AdminDashboard /> : <Landing />}
      </Route>
      <Route path="/dashboard">
        {user ? <UserDashboard /> : <Landing />}
      </Route>
      <Route>
        <Landing />
      </Route>
    </Switch>
  );
}

function App() {
  return (
    <QueryClientProvider client={queryClient}>
      <AuthProvider>
        <TooltipProvider>
          <Toaster />
          <AppContent />
        </TooltipProvider>
      </AuthProvider>
    </QueryClientProvider>
  );
}

export default App;
