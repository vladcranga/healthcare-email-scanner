import React, { useEffect, useState } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { FaArrowLeft } from 'react-icons/fa';
import { emailService } from '../services/api';
import Navbar from '../components/Navbar';
import StatusBadge from '../components/StatusBadge';

interface Email {
  id: number;
  sender: string;
  subject: string;
  content: string;
  status: 'safe' | 'suspicious' | 'dangerous';
  confidence_score: number | null;
  received_date: string;
  is_quarantined: boolean;
}

const EmailDetailPage: React.FC = () => {
  const { id } = useParams<{ id: string }>();
  const navigate = useNavigate();
  const [email, setEmail] = useState<Email | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const fetchEmail = async () => {
      try {
        const response = await emailService.getEmail(Number(id));
        setEmail(response.data);
      } catch (err) {
        setError('Failed to load email details');
        console.error('Error fetching email:', err);
      } finally {
        setLoading(false);
      }
    };

    fetchEmail();
  }, [id]);

  if (loading) {
    return (
      <div className="min-h-screen bg-gray-100">
        <Navbar />
        <div className="container mx-auto px-4 py-8">
          <div className="text-center">Loading...</div>
        </div>
      </div>
    );
  }

  if (error || !email) {
    return (
      <div className="min-h-screen bg-gray-100">
        <Navbar />
        <div className="container mx-auto px-4 py-8">
          <div className="text-center text-red-600">{error || 'Email not found'}</div>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-100">
      <Navbar />
      <div className="container mx-auto px-4 py-8">
        {/* Back button */}
        <button
          onClick={() => navigate('/dashboard')}
          className="mb-6 inline-flex items-center px-4 py-2 border border-transparent shadow-sm text-sm font-medium rounded-md text-white bg-blue-600 hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500"
        >
          <FaArrowLeft className="mr-2 -ml-0.5 h-4 w-4" />
          Back to Dashboard
        </button>

        {/* Email details card */}
        <div className="bg-white rounded-lg shadow-md p-6">
          <div className="border-b pb-4 mb-4">
            <h1 className="text-2xl font-bold mb-2">{email.subject}</h1>
            <div className="flex items-center justify-between flex-wrap gap-2">
              <div className="text-gray-600">From: {email.sender}</div>
              <div className="text-gray-600">
                Received at: {new Date(email.received_date).toLocaleString()}
              </div>
            </div>
          </div>

          {/* Status and security info */}
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4 mb-6">
            <div className="p-4 bg-gray-50 rounded-lg">
              <div className="text-sm text-gray-600 mb-1">Status</div>
              <StatusBadge status={email.status} />
            </div>
            <div className="p-4 bg-gray-50 rounded-lg">
              <div className="text-sm text-gray-600 mb-1">Confidence Score</div>
              <div>{email.confidence_score !== null ? `${(email.confidence_score * 100).toFixed(1)}%` : 'N/A'}</div>
            </div>
          </div>

          {/* Email content */}
          <div>
            <h2 className="text-lg font-semibold mb-3">Content</h2>
            <div className="bg-gray-50 p-4 rounded-lg whitespace-pre-wrap">
              {email.content}
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default EmailDetailPage;
