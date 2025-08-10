import React, { useState } from 'react';
import {
  EnvelopeIcon,
  ChartBarIcon,
  CogIcon,
  CheckCircleIcon,
  XCircleIcon,
} from '@heroicons/react/24/outline';

const Notifications: React.FC = () => {
  const [activeTab, setActiveTab] = useState('preferences');

  const tabs = [
    { id: 'preferences', name: 'Email Preferences', icon: CogIcon },
    { id: 'logs', name: 'Email Logs', icon: EnvelopeIcon },
    { id: 'statistics', name: 'Email Statistics', icon: ChartBarIcon },
  ];

  return (
    <div className="w-full max-w-6xl mx-auto space-y-4 sm:space-y-6 px-0">
      <div className="px-4 sm:px-0">
        <h1 className="text-xl sm:text-2xl font-bold text-ocean-deep">Notification Center</h1>
        <p className="mt-2 text-sm text-neutral">
          Manage your email preferences and view notification history.
        </p>
      </div>

      <div className="bg-white/95 backdrop-blur-sm shadow-sm border border-mist/20 rounded-xl mx-4 sm:mx-0 overflow-hidden">
        {/* Tab Navigation */}
        <div className="border-b border-mist/20">
          <nav className="flex px-2 sm:px-6 overflow-x-auto scrollbar-hide">
            {tabs.map((tab) => (
              <button
                key={tab.id}
                onClick={() => setActiveTab(tab.id)}
                className={`flex items-center py-3 sm:py-4 px-3 sm:px-1 border-b-2 font-medium text-xs sm:text-sm whitespace-nowrap transition-all duration-200 ${
                  activeTab === tab.id
                    ? 'border-atlantic text-atlantic'
                    : 'border-transparent text-neutral hover:text-ocean-deep hover:border-mist'
                }`}
              >
                <tab.icon className="h-4 w-4 sm:h-5 sm:w-5 mr-1 sm:mr-2 flex-shrink-0" />
                <span className="hidden sm:inline">{tab.name}</span>
                <span className="sm:hidden">{tab.name.split(' ')[0]}</span>
              </button>
            ))}
          </nav>
        </div>

        <div className="p-4 sm:p-6">
          {activeTab === 'preferences' && (
            <div className="space-y-4 sm:space-y-6">
              <div>
                <h3 className="text-base sm:text-lg font-medium text-ocean-deep">Email Notification Preferences</h3>
                <p className="mt-1 text-sm text-neutral">
                  Choose which notifications you'd like to receive via email.
                </p>
              </div>

              <div className="space-y-4">
                <div className="relative flex items-start">
                  <div className="flex items-center h-5 mt-1">
                    <input
                      id="project-submitted"
                      type="checkbox"
                      className="focus:ring-atlantic h-4 w-4 text-atlantic border-mist rounded"
                      defaultChecked
                    />
                  </div>
                  <div className="ml-3 text-sm flex-1 min-w-0">
                    <label htmlFor="project-submitted" className="font-medium text-ocean-deep block cursor-pointer">
                      Project Submissions
                    </label>
                    <p className="text-neutral mt-1">Get notified when projects are submitted for review.</p>
                  </div>
                </div>

                <div className="relative flex items-start">
                  <div className="flex items-center h-5 mt-1">
                    <input
                      id="project-approved"
                      type="checkbox"
                      className="focus:ring-atlantic h-4 w-4 text-atlantic border-mist rounded"
                      defaultChecked
                    />
                  </div>
                  <div className="ml-3 text-sm flex-1 min-w-0">
                    <label htmlFor="project-approved" className="font-medium text-ocean-deep block cursor-pointer">
                      Project Approvals
                    </label>
                    <p className="text-neutral mt-1">Get notified when your projects are approved.</p>
                  </div>
                </div>

                <div className="relative flex items-start">
                  <div className="flex items-center h-5 mt-1">
                    <input
                      id="project-rejected"
                      type="checkbox"
                      className="focus:ring-atlantic h-4 w-4 text-atlantic border-mist rounded"
                      defaultChecked
                    />
                  </div>
                  <div className="ml-3 text-sm flex-1 min-w-0">
                    <label htmlFor="project-rejected" className="font-medium text-ocean-deep block cursor-pointer">
                      Project Rejections
                    </label>
                    <p className="text-neutral mt-1">Get notified when your projects are rejected.</p>
                  </div>
                </div>

                <div className="relative flex items-start">
                  <div className="flex items-center h-5 mt-1">
                    <input
                      id="revision-required"
                      type="checkbox"
                      className="focus:ring-atlantic h-4 w-4 text-atlantic border-mist rounded"
                      defaultChecked
                    />
                  </div>
                  <div className="ml-3 text-sm flex-1 min-w-0">
                    <label htmlFor="revision-required" className="font-medium text-ocean-deep block cursor-pointer">
                      Revision Requests
                    </label>
                    <p className="text-neutral mt-1">Get notified when revisions are requested.</p>
                  </div>
                </div>
              </div>

              <div className="flex justify-end pt-2">
                <button className="bg-atlantic text-white px-4 sm:px-6 py-2 sm:py-3 rounded-xl hover:bg-ocean-deep focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-atlantic transition-all duration-200 font-medium text-sm">
                  Save Preferences
                </button>
              </div>
            </div>
          )}

          {activeTab === 'logs' && (
            <div className="space-y-4 sm:space-y-6">
              <div>
                <h3 className="text-base sm:text-lg font-medium text-ocean-deep">Recent Email Notifications</h3>
                <p className="mt-1 text-sm text-neutral">
                  View the history of email notifications sent to your account.
                </p>
              </div>

              {/* Mobile Card Layout */}
              <div className="block sm:hidden space-y-3">
                <div className="bg-white border border-mist/20 rounded-lg p-4 shadow-sm">
                  <div className="flex items-center justify-between mb-2">
                    <div className="flex items-center">
                      <CheckCircleIcon className="h-5 w-5 text-success mr-2 flex-shrink-0" />
                      <span className="text-sm font-medium text-ocean-deep">Delivered</span>
                    </div>
                    <span className="inline-flex items-center px-2 py-1 rounded-full text-xs font-medium bg-success/10 text-success">
                      Approval
                    </span>
                  </div>
                  <p className="text-sm text-ocean-deep mb-1 font-medium">Project "Building Design" has been approved</p>
                  <p className="text-xs text-neutral">{new Date().toLocaleDateString()}</p>
                </div>
                
                <div className="bg-white border border-mist/20 rounded-lg p-4 shadow-sm">
                  <div className="flex items-center justify-between mb-2">
                    <div className="flex items-center">
                      <CheckCircleIcon className="h-5 w-5 text-success mr-2 flex-shrink-0" />
                      <span className="text-sm font-medium text-ocean-deep">Delivered</span>
                    </div>
                    <span className="inline-flex items-center px-2 py-1 rounded-full text-xs font-medium bg-atlantic/10 text-atlantic">
                      Submission
                    </span>
                  </div>
                  <p className="text-sm text-ocean-deep mb-1 font-medium">New project submission requires review</p>
                  <p className="text-xs text-neutral">{new Date(Date.now() - 86400000).toLocaleDateString()}</p>
                </div>
              </div>

              {/* Desktop Table Layout */}
              <div className="hidden sm:block overflow-hidden shadow-sm ring-1 ring-mist/20 rounded-xl">
                <table className="min-w-full divide-y divide-mist/20">
                  <thead className="bg-mist/5">
                    <tr>
                      <th className="px-6 py-3 text-left text-xs font-medium text-neutral uppercase tracking-wider">
                        Status
                      </th>
                      <th className="px-6 py-3 text-left text-xs font-medium text-neutral uppercase tracking-wider">
                        Subject
                      </th>
                      <th className="px-6 py-3 text-left text-xs font-medium text-neutral uppercase tracking-wider">
                        Date Sent
                      </th>
                      <th className="px-6 py-3 text-left text-xs font-medium text-neutral uppercase tracking-wider">
                        Type
                      </th>
                    </tr>
                  </thead>
                  <tbody className="bg-white divide-y divide-mist/10">
                    <tr className="hover:bg-mist/5 transition-colors">
                      <td className="px-6 py-4 whitespace-nowrap">
                        <span className="flex items-center">
                          <CheckCircleIcon className="h-5 w-5 text-success mr-2" />
                          <span className="text-sm text-ocean-deep">Delivered</span>
                        </span>
                      </td>
                      <td className="px-6 py-4 text-sm text-ocean-deep">
                        Project "Building Design" has been approved
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap text-sm text-neutral">
                        {new Date().toLocaleDateString()}
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap">
                        <span className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-success/10 text-success">
                          Approval
                        </span>
                      </td>
                    </tr>
                    <tr className="hover:bg-mist/5 transition-colors">
                      <td className="px-6 py-4 whitespace-nowrap">
                        <span className="flex items-center">
                          <CheckCircleIcon className="h-5 w-5 text-success mr-2" />
                          <span className="text-sm text-ocean-deep">Delivered</span>
                        </span>
                      </td>
                      <td className="px-6 py-4 text-sm text-ocean-deep">
                        New project submission requires review
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap text-sm text-neutral">
                        {new Date(Date.now() - 86400000).toLocaleDateString()}
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap">
                        <span className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-atlantic/10 text-atlantic">
                          Submission
                        </span>
                      </td>
                    </tr>
                  </tbody>
                </table>
              </div>
            </div>
          )}

          {activeTab === 'statistics' && (
            <div className="space-y-4 sm:space-y-6">
              <div>
                <h3 className="text-base sm:text-lg font-medium text-ocean-deep">Email Statistics</h3>
                <p className="mt-1 text-sm text-neutral">
                  Overview of email notifications and delivery rates.
                </p>
              </div>

              <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4 sm:gap-6">
                <div className="bg-atlantic/5 rounded-xl p-4 sm:p-6 border border-atlantic/10">
                  <div className="flex items-center">
                    <EnvelopeIcon className="h-6 w-6 sm:h-8 sm:w-8 text-atlantic flex-shrink-0" />
                    <div className="ml-3 sm:ml-4 min-w-0 flex-1">
                      <p className="text-xs sm:text-sm font-medium text-atlantic">Total Sent</p>
                      <p className="text-xl sm:text-2xl font-bold text-ocean-deep">156</p>
                    </div>
                  </div>
                </div>

                <div className="bg-success/5 rounded-xl p-4 sm:p-6 border border-success/10">
                  <div className="flex items-center">
                    <CheckCircleIcon className="h-6 w-6 sm:h-8 sm:w-8 text-success flex-shrink-0" />
                    <div className="ml-3 sm:ml-4 min-w-0 flex-1">
                      <p className="text-xs sm:text-sm font-medium text-success">Delivered</p>
                      <p className="text-xl sm:text-2xl font-bold text-ocean-deep">154</p>
                    </div>
                  </div>
                </div>

                <div className="bg-error/5 rounded-xl p-4 sm:p-6 border border-error/10 sm:col-span-2 lg:col-span-1">
                  <div className="flex items-center">
                    <XCircleIcon className="h-6 w-6 sm:h-8 sm:w-8 text-error flex-shrink-0" />
                    <div className="ml-3 sm:ml-4 min-w-0 flex-1">
                      <p className="text-xs sm:text-sm font-medium text-error">Failed</p>
                      <p className="text-xl sm:text-2xl font-bold text-ocean-deep">2</p>
                    </div>
                  </div>
                </div>
              </div>

              <div className="bg-mist/5 border border-mist/20 rounded-xl p-4 sm:p-6">
                <h4 className="text-base sm:text-lg font-medium text-ocean-deep mb-4">Delivery Rate</h4>
                <div className="w-full bg-mist/30 rounded-full h-2 sm:h-3">
                  <div className="bg-success h-2 sm:h-3 rounded-full transition-all duration-500" style={{ width: '98.7%' }}></div>
                </div>
                <p className="text-sm text-neutral mt-2">98.7% delivery rate</p>
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  );
};

export default Notifications;