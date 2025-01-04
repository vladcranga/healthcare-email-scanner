import React, { useState, useEffect } from "react";
import {
  FaEnvelope,
  FaShieldAlt,
  FaShieldVirus,
  FaExclamationTriangle,
  FaSearch,
  FaTrash,
} from "react-icons/fa";
import { emailService } from "../services/api";
import Navbar from "../components/Navbar";
import { useNavigate } from "react-router-dom";
import StatusBadge from "../components/StatusBadge";
import ImportExportPanel from "../components/ImportExportPanel";
import WarningModal from "../components/WarningModal";

// Types for email and statistics
interface Email {
  id: number;
  sender: string;
  subject: string;
  content: string;
  status: "safe" | "suspicious" | "dangerous";
  confidence_score: number | null;
  received_date: string;
  is_quarantined: boolean;
  has_attachments: boolean;
}

interface DashboardStats {
  total_emails: number;
  suspicious_emails: number;
  detection_rate: number;
  high_risk_emails: number;
}

const StatCard: React.FC<{
  icon: React.ReactNode;
  title: string;
  value: string | number;
}> = ({ icon, title, value }) => (
  <div className="bg-white p-6 rounded-lg shadow-md flex items-center space-x-4">
    <div className="text-5xl text-indigo-600 flex">{icon}</div>
    <div>
      <h3 className="text-sm font-medium text-gray-500 truncate">{title}</h3>
      <p className="mt-1 text-3xl font-semibold text-gray-900">{value}</p>
    </div>
  </div>
);

const DashboardPage: React.FC = () => {
  const [emails, setEmails] = useState<Email[]>([]);
  const [stats, setStats] = useState<DashboardStats>({
    total_emails: 0,
    suspicious_emails: 0,
    detection_rate: 0,
    high_risk_emails: 0,
  });
  const [searchTerm, setSearchTerm] = useState("");
  const [statusFilter, setStatusFilter] = useState<
    "all" | "safe" | "suspicious" | "dangerous"
  >("all");
  const [currentPage, setCurrentPage] = useState(1);
  const [totalPages, setTotalPages] = useState(1);
  const navigate = useNavigate();
  const [selectedEmail, setSelectedEmail] = useState<Email | null>(null);
  const [showWarningModal, setShowWarningModal] = useState(false);

  const fetchDashboardData = async () => {
    try {
      // Fetch all emails with optional status filter
      const emailsResponse = await emailService.getEmails({
        status: statusFilter === "all" ? undefined : statusFilter,
        search: searchTerm || undefined,
        page: currentPage,
      });

      if (emailsResponse.data.results) {
        setEmails(emailsResponse.data.results);
        setTotalPages(Math.ceil(emailsResponse.data.count / 10));
      } else {
        console.error("Unexpected emails data format", emailsResponse.data);
        setEmails([]);
        setTotalPages(1);
      }

      // Fetch dashboard statistics
      const statsResponse = await emailService.getSuspiciousSummary();
      setStats(statsResponse.data);
    } catch (error) {
      console.error("Failed to fetch dashboard data", error);
    }
  };

  useEffect(() => {
    fetchDashboardData();
  }, [searchTerm, statusFilter, currentPage]);

  const handleEmailClick = (email: Email) => {
    if (email.status === "suspicious" || email.status === "dangerous") {
      setSelectedEmail(email);
      setShowWarningModal(true);
    } else {
      navigate(`/emails/${email.id}`);
    }
  };

  const handleDeleteEmail = async (e: React.MouseEvent, emailId: number) => {
    e.stopPropagation(); // Prevent row click event
    if (window.confirm("Are you sure you want to delete this email?")) {
      try {
        await emailService.deleteEmail(emailId);
        fetchDashboardData(); // Refresh the list
      } catch (error) {
        console.error("Failed to delete email:", error);
      }
    }
  };

  return (
    <div className="min-h-screen bg-gray-100">
      <Navbar />
      <div className="py-6">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          {/* Stats Grid */}
          <dl className="grid grid-cols-1 gap-5 sm:grid-cols-2 lg:grid-cols-4 mb-8">
            <StatCard
              title="Total Emails"
              value={stats.total_emails}
              icon={<FaEnvelope />}
            />
            <StatCard
              title="Safe Emails"
              value={Math.max(
                0,
                stats.total_emails -
                  stats.suspicious_emails -
                  stats.high_risk_emails,
              )}
              icon={<FaShieldAlt />}
            />
            <StatCard
              title="Suspicious Emails"
              value={stats.suspicious_emails}
              icon={<FaShieldVirus />}
            />
            <StatCard
              title="High-Risk Emails"
              value={stats.high_risk_emails}
              icon={<FaExclamationTriangle />}
            />
          </dl>

          {/* Import/Export Panel */}
          <ImportExportPanel
            hasEmails={stats.total_emails > 0}
            onImportSuccess={() => {
              setCurrentPage(1);
              fetchDashboardData();
            }}
          />

          {/* Main Content */}
          <div className="bg-white shadow rounded-lg p-6">
            <div className="flex justify-between items-center mb-6">
              <div className="space-y-2">
                <h2 className="text-2xl font-bold text-gray-800">Emails</h2>

                {/* Status Filter Buttons */}
                <div className="flex space-x-2 mb-4">
                  <button
                    onClick={() => {
                      setStatusFilter("all");
                      setCurrentPage(1);
                    }}
                    className={`px-4 py-2 rounded-md ${
                      statusFilter === "all"
                        ? "bg-blue-500 text-white"
                        : "bg-gray-200 text-gray-700"
                    }`}
                  >
                    All
                  </button>
                  <button
                    onClick={() => {
                      setStatusFilter("safe");
                      setCurrentPage(1);
                    }}
                    className={`px-4 py-2 rounded-md ${
                      statusFilter === "safe"
                        ? "bg-green-500 text-white"
                        : "bg-gray-200 text-gray-700"
                    }`}
                  >
                    Safe
                  </button>
                  <button
                    onClick={() => {
                      setStatusFilter("suspicious");
                      setCurrentPage(1);
                    }}
                    className={`px-4 py-2 rounded-md ${
                      statusFilter === "suspicious"
                        ? "bg-yellow-500 text-white"
                        : "bg-gray-200 text-gray-700"
                    }`}
                  >
                    Suspicious
                  </button>
                  <button
                    onClick={() => {
                      setStatusFilter("dangerous");
                      setCurrentPage(1);
                    }}
                    className={`px-4 py-2 rounded-md ${
                      statusFilter === "dangerous"
                        ? "bg-red-500 text-white"
                        : "bg-gray-200 text-gray-700"
                    }`}
                  >
                    Dangerous
                  </button>
                </div>
              </div>

              {/* Search Input */}
              <div className="relative">
                <input
                  type="text"
                  placeholder="Search emails..."
                  value={searchTerm}
                  onChange={(e) => setSearchTerm(e.target.value)}
                  className="pl-10 pr-4 py-2 border rounded-lg w-64 focus:outline-none focus:ring-2 focus:ring-blue-500"
                />
                <FaSearch className="absolute left-3 top-3.5 text-gray-400" />
              </div>
            </div>

            {/* Emails Table */}
            <div className="overflow-x-auto">
              <table className="min-w-full divide-y divide-gray-200">
                <thead className="bg-gray-100">
                  <tr>
                    <th className="p-3 text-left">Sender</th>
                    <th className="p-3 text-left">Subject</th>
                    <th className="p-3 text-left">Received Date</th>
                    <th className="p-3 text-left">Status</th>
                    <th className="p-3 text-left">Action</th>
                  </tr>
                </thead>
                <tbody>
                  {emails.length === 0 ? (
                    <tr>
                      <td
                        colSpan={5}
                        className="text-center py-4 text-gray-500"
                      >
                        No emails found
                      </td>
                    </tr>
                  ) : (
                    emails.map((email) => (
                      <tr
                        key={email.id}
                        className="border-b hover:bg-gray-100 cursor-pointer"
                        onClick={() => handleEmailClick(email)}
                      >
                        <td className="p-3">{email.sender}</td>
                        <td className="p-3">{email.subject}</td>
                        <td className="p-3">
                          {new Date(email.received_date).toLocaleDateString()}
                        </td>
                        <td className="p-3">
                          <StatusBadge status={email.status} />
                        </td>
                        <td className="p-3">
                          <button
                            onClick={(e) => handleDeleteEmail(e, email.id)}
                            className="text-red-600 hover:text-red-800 transition-colors"
                            title="Delete Email"
                          >
                            <FaTrash />
                          </button>
                        </td>
                      </tr>
                    ))
                  )}
                </tbody>
              </table>

              {/* Pagination Controls */}
              <div className="flex items-center justify-between border-t border-gray-200 bg-white px-4 py-3 sm:px-6 mt-4">
                <div className="flex flex-1 justify-between sm:hidden">
                  <button
                    onClick={() =>
                      setCurrentPage((prev) => Math.max(prev - 1, 1))
                    }
                    disabled={currentPage === 1}
                    className="relative inline-flex items-center rounded-md border border-gray-300 bg-white px-4 py-2 text-sm font-medium text-gray-700 hover:bg-gray-50 disabled:opacity-50"
                  >
                    Previous
                  </button>
                  <button
                    onClick={() =>
                      setCurrentPage((prev) => Math.min(prev + 1, totalPages))
                    }
                    disabled={currentPage === totalPages}
                    className="relative ml-3 inline-flex items-center rounded-md border border-gray-300 bg-white px-4 py-2 text-sm font-medium text-gray-700 hover:bg-gray-50 disabled:opacity-50"
                  >
                    Next
                  </button>
                </div>
                <div className="hidden sm:flex sm:flex-1 sm:items-center sm:justify-between">
                  <div>
                    <p className="text-sm text-gray-700">
                      Showing page{" "}
                      <span className="font-medium">{currentPage}</span> of{" "}
                      <span className="font-medium">{totalPages}</span>
                    </p>
                  </div>
                  <div>
                    <nav
                      className="isolate inline-flex -space-x-px rounded-md shadow-sm"
                      aria-label="Pagination"
                    >
                      <button
                        onClick={() =>
                          setCurrentPage((prev) => Math.max(prev - 1, 1))
                        }
                        disabled={currentPage === 1}
                        className="relative inline-flex items-center rounded-l-md px-2 py-2 text-gray-400 ring-1 ring-inset ring-gray-300 hover:bg-gray-50 focus:z-20 focus:outline-offset-0 disabled:opacity-50"
                      >
                        <span className="sr-only">Previous</span>
                        <svg
                          className="h-5 w-5"
                          viewBox="0 0 20 20"
                          fill="currentColor"
                          aria-hidden="true"
                        >
                          <path
                            fillRule="evenodd"
                            d="M12.79 5.23a.75.75 0 01-.02 1.06L8.832 10l3.938 3.71a.75.75 0 11-1.04 1.08l-4.5-4.25a.75.75 0 010-1.08l4.5-4.25a.75.75 0 011.06.02z"
                            clipRule="evenodd"
                          />
                        </svg>
                      </button>
                      <button
                        onClick={() =>
                          setCurrentPage((prev) =>
                            Math.min(prev + 1, totalPages),
                          )
                        }
                        disabled={currentPage === totalPages}
                        className="relative inline-flex items-center rounded-r-md px-2 py-2 text-gray-400 ring-1 ring-inset ring-gray-300 hover:bg-gray-50 focus:z-20 focus:outline-offset-0 disabled:opacity-50"
                      >
                        <span className="sr-only">Next</span>
                        <svg
                          className="h-5 w-5"
                          viewBox="0 0 20 20"
                          fill="currentColor"
                          aria-hidden="true"
                        >
                          <path
                            fillRule="evenodd"
                            d="M7.21 14.77a.75.75 0 01.02-1.06L11.168 10 7.23 6.29a.75.75 0 111.04-1.08l4.5 4.25a.75.75 0 010 1.08l-4.5 4.25a.75.75 0 01-1.06-.02z"
                            clipRule="evenodd"
                          />
                        </svg>
                      </button>
                    </nav>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
      {/* Warning Modal */}
      <WarningModal
        isOpen={showWarningModal}
        onClose={() => setShowWarningModal(false)}
        onConfirm={() => {
          setShowWarningModal(false);
          if (selectedEmail) {
            navigate(`/emails/${selectedEmail.id}`);
          }
        }}
        emailStatus={selectedEmail?.status as "suspicious" | "dangerous"}
      />
    </div>
  );
};

export default DashboardPage;
