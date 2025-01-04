import React from "react";

const StatusBadge: React.FC<{ status: string }> = ({ status }) => {
  const getBadgeColor = () => {
    switch (status.toLowerCase()) {
      case "suspicious":
        return "bg-yellow-100 text-yellow-800";
      case "dangerous":
        return "bg-red-100 text-red-800";
      case "safe":
        return "bg-green-100 text-green-800";
      default:
        return "bg-gray-100 text-gray-800";
    }
  };

  return (
    <span
      className={`px-2 py-1 rounded-full text-xs font-bold ${getBadgeColor()}`}
    >
      {status.charAt(0).toUpperCase() + status.slice(1)}
    </span>
  );
};

export default StatusBadge;
