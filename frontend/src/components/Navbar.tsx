import React from "react";
import { useNavigate } from "react-router-dom";
import { useAppSelector, useAppDispatch } from "../store";
import { FaUserCircle, FaSignOutAlt } from "react-icons/fa";
import { authService } from "../services/api";
import { logout } from "../store/authSlice";

const Navbar: React.FC = () => {
  const navigate = useNavigate();
  const dispatch = useAppDispatch();
  const { user } = useAppSelector((state) => state.auth);

  const handleLogout = async () => {
    try {
      await authService.logout();
      dispatch(logout());
      navigate("/");
    } catch (error) {
      console.error("Logout failed:", error);
      // Still logout locally even if backend fails
      dispatch(logout());
      navigate("/");
    }
  };

  return (
    <nav className="bg-white shadow-lg">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex justify-between h-16">
          {/* Logo/Brand */}
          <div className="flex items-center">
            <span
              className="text-xl font-semibold text-indigo-600 cursor-pointer"
              onClick={() => navigate("/dashboard")}
            >
              Healthcare Email Scanner
            </span>
          </div>

          {/* User Info & Logout */}
          <div className="flex items-center space-x-4">
            <div className="flex items-center space-x-2">
              <FaUserCircle className="text-gray-500 text-xl" />
              <span className="text-gray-700">
                Welcome, {user?.name || user?.email?.split("@")[0] || "User"}
              </span>
            </div>
            <button
              onClick={handleLogout}
              className="flex items-center space-x-1 px-4 py-2 rounded-md text-gray-700 hover:bg-gray-100 transition-colors"
            >
              <FaSignOutAlt />
              <span>Logout</span>
            </button>
          </div>
        </div>
      </div>
    </nav>
  );
};

export default Navbar;
