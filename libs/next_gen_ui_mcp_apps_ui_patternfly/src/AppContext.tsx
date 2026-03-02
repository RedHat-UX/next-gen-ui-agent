import { createContext, useContext, type ReactNode } from "react";
import type { App } from "@modelcontextprotocol/ext-apps";

const McpAppContext = createContext<App | null>(null);

export function useMcpApp(): App | null {
  return useContext(McpAppContext);
}

export function AppContextProvider({
  app,
  children,
}: {
  app: App | null;
  children: ReactNode;
}) {
  return (
    <McpAppContext.Provider value={app}>{children}</McpAppContext.Provider>
  );
}
