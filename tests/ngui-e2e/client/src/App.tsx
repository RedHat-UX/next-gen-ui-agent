import ChatBotPage from "./components/ChatBot";

function App() {
  return (
    <div>
      <h1>NGUI Web Components PoC</h1>

      {/* Test: Render ngui-card directly in React */}
      <ngui-card title="Test Card - Direct Render">
        <dl slot="content">
          <dt>Framework</dt>
          <dd>Platform-native Web Components</dd>
          <dt>Status</dt>
          <dd>Working in React!</dd>
          <dt>PoC Goal</dt>
          <dd>Prove web components work without React wrappers</dd>
        </dl>
      </ngui-card>

      <hr style={{ margin: '2rem 0' }} />

      <ChatBotPage />
    </div>
  );
}

export default App;
