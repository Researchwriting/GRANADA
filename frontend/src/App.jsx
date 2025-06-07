import React, { useState } from 'react'

function Tab({ name, activeTab, setActiveTab }) {
  return (
    <button
      className={`px-4 py-2 ${activeTab === name ? 'bg-blue-500 text-white' : 'bg-gray-200'}`}
      onClick={() => setActiveTab(name)}
    >
      {name}
    </button>
  )
}

function App() {
  const tabs = ['Proposal', 'Donor Matching', 'Logframe', 'Budget', 'Downloads']
  const [activeTab, setActiveTab] = useState(tabs[0])
  return (
    <div className="p-4">
      <h1 className="text-2xl font-bold mb-4">GRANADA Dashboard</h1>
      <div className="flex space-x-2 mb-4">
        {tabs.map(t => <Tab key={t} name={t} activeTab={activeTab} setActiveTab={setActiveTab} />)}
      </div>
      <div className="p-4 bg-white shadow">
        <p>{activeTab} content goes here.</p>
      </div>
    </div>
  )
}

export default App
