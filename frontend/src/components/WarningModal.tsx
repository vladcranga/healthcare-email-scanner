import React from "react";
import { FaExclamationTriangle } from "react-icons/fa";

interface WarningModalProps {
  isOpen: boolean;
  onClose: () => void;
  onConfirm: () => void;
  emailStatus: "suspicious" | "dangerous";
}

const WarningModal: React.FC<WarningModalProps> = ({
  isOpen,
  onClose,
  onConfirm,
  emailStatus,
}) => {
  if (!isOpen) return null;

  const getStatusColor = () => {
    return emailStatus === "dangerous" ? "red" : "yellow";
  };

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 z-50 flex items-center justify-center">
      <div className="bg-white rounded-lg p-6 max-w-md w-full mx-4">
        <div className={`text-${getStatusColor()}-600 text-center mb-4`}>
          <FaExclamationTriangle className="text-5xl mx-auto" />
        </div>

        <h2
          className={`text-2xl font-bold text-${getStatusColor()}-600 text-center mb-4`}
        >
          {emailStatus === "dangerous"
            ? "Warning: Dangerous Email"
            : "Caution: Suspicious Email"}
        </h2>

        <p className="text-gray-600 mb-6 text-center">
          {emailStatus === "dangerous"
            ? "This email has been flagged as dangerous and may contain malicious content. Opening it could pose a security risk."
            : "This email has been flagged as suspicious. Please proceed with caution."}
        </p>

        <div className="flex justify-center space-x-4">
          <button
            onClick={onClose}
            className="px-4 py-2 bg-green-600 text-white rounded hover:bg-green-500 transition-colors"
          >
            Go Back
          </button>
          <button
            onClick={onConfirm}
            className={`px-4 py-2 bg-red-600 text-white rounded hover:bg-red-500 transition-colors`}
          >
            Open Anyway
          </button>
        </div>
      </div>
    </div>
  );
};

export default WarningModal;
