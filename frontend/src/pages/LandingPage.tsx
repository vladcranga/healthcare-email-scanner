import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { FaShieldAlt, FaEnvelope, FaChartLine, FaRobot } from 'react-icons/fa';
import { emailService } from '../services/api';

const StatCard: React.FC<{ icon: React.ReactNode; value: string; label: string }> = ({ icon, value, label }) => (
  <div className="bg-white p-6 rounded-lg shadow-md flex items-center space-x-4 transform transition hover:scale-105">
    <div className="text-4xl text-indigo-600">{icon}</div>
    <div>
      <h3 className="text-3xl font-bold text-gray-800">{value}</h3>
      <p className="text-gray-500">{label}</p>
    </div>
  </div>
);

const FeatureCard: React.FC<{ icon: React.ReactNode; title: string; description: string }> = ({ icon, title, description }) => (
  <div className="bg-white p-6 rounded-lg shadow-md text-center transform transition hover:scale-105">
    <div className="text-5xl text-indigo-600 mb-4 flex justify-center">{icon}</div>
    <h3 className="text-xl font-semibold mb-3">{title}</h3>
    <p className="text-gray-600">{description}</p>
  </div>
);

const LandingPage: React.FC = () => {
  const navigate = useNavigate();
  const [stats, setStats] = useState({
    totalEmails: '0',
    suspiciousEmails: '0',
    dangerousEmails: '0',
    problematicEmails: '0',
    detectionRate: '0%'
  });

  useEffect(() => {
    const fetchStats = async () => {
      try {
        const response = await emailService.getPublicStats();
        const { total_emails, suspicious_emails, high_risk_emails, detection_rate } = response.data;
        
        setStats({
          totalEmails: total_emails.toLocaleString(),
          suspiciousEmails: suspicious_emails.toLocaleString(),
          dangerousEmails: high_risk_emails.toLocaleString(),
          problematicEmails: (suspicious_emails + high_risk_emails).toLocaleString(),
          detectionRate: `${(detection_rate * 100).toFixed(2)}%`
        });
      } catch (error) {
        console.error('Failed to fetch email statistics', error);
      }
    };

    fetchStats();
  }, []);

  return (
    <div className="min-h-screen bg-gray-100 py-12">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        {/* Hero Section */}
        <header className="bg-gradient-to-r from-indigo-600 to-purple-600 text-white">
          <div className="container mx-auto px-4 py-20 text-center">
            <h1 className="text-5xl font-extrabold mb-6">Healthcare Email Scanner</h1>
            <p className="text-xl mb-8">Protect sensitive medical communications with ML-powered threat detection and classification</p>
            <div className="space-x-4">
              <button 
                onClick={() => navigate('/register')}
                className="bg-white text-indigo-600 px-8 py-3 rounded-full font-bold hover:bg-gray-100 transition"
              >
                Get Started
              </button>
              <button 
                onClick={() => navigate('/login')}
                className="border-2 border-white text-white px-8 py-3 rounded-full font-bold hover:bg-white hover:text-indigo-600 transition"
              >
                Login
              </button>
            </div>
          </div>
        </header>

        {/* Statistics Section */}
        <section className="container mx-auto px-4 -mt-16 mb-16">
          <div className="grid md:grid-cols-3 gap-6">
            <StatCard 
              icon={<FaEnvelope />} 
              value={stats.totalEmails} 
              label="Total Emails Analyzed" 
            />
            <StatCard 
              icon={<FaShieldAlt />} 
              value={stats.problematicEmails} 
              label="Problematic Emails Detected" 
            />
            <StatCard 
              icon={<FaChartLine />} 
              value={stats.detectionRate} 
              label="Detection Accuracy" 
            />
          </div>
        </section>

        {/* Features Section */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          <FeatureCard 
            icon={<FaRobot />} 
            title="Smart Email Classification" 
            description="Our machine learning system classifies healthcare emails as safe, suspicious, or dangerous with over 80% accuracy."
          />
          <FeatureCard 
            icon={<FaChartLine />} 
            title="Risk Analytics Dashboard" 
            description="Monitor email security with statistics, confidence scores, and threat detection rates specific to healthcare communications."
          />
          <FeatureCard 
            icon={<FaShieldAlt />} 
            title="Healthcare-Specific Protection" 
            description="Specialised detection of medical scams, phishing attempts, and sensitive data exposure in healthcare context."
          />
        </div>

        {/* Call to Action */}
        <section className="bg-indigo-600 text-white py-20 text-center">
          <h2 className="text-4xl font-bold mb-6">Protect Your Communications</h2>
          <p className="text-xl mb-8">Join healthcare providers in protecting sensitive medical correspondence from emerging threats</p>
          <button 
            onClick={() => navigate('/register')}
            className="bg-white text-indigo-600 px-10 py-4 rounded-full text-xl font-bold hover:bg-gray-100 transition"
          >
            Sign Up
          </button>
        </section>
      </div>
    </div>
  );
};

export default LandingPage;
