import ChatBotPage from "./components/ChatBot";
import { ComponentHandlerRegistryProvider } from '@rhngui/patternfly-react-renderer';

function App() {
  return (
    <ComponentHandlerRegistryProvider>
      <div className="app-container">
        <ChatBotPage />
      </div>
    </ComponentHandlerRegistryProvider>
  );
}

export default App;
