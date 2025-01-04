import { createSlice, createAsyncThunk } from "@reduxjs/toolkit";
import { authService } from "../services/api";

interface AuthState {
  user: {
    email: string | null;
    name: string | null;
  } | null;
  isAuthenticated: boolean;
  isLoading: boolean;
  error: string | null;
}

const initialState: AuthState = {
  user: localStorage.getItem("userEmail")
    ? {
        email: localStorage.getItem("userEmail"),
        name: localStorage.getItem("userEmail")?.split("@")[0] || null,
      }
    : null,
  isAuthenticated: !!localStorage.getItem("token"),
  isLoading: false,
  error: null,
};

export const loginUser = createAsyncThunk(
  "auth/loginUser",
  async (
    { email, password }: { email: string; password: string },
    { rejectWithValue },
  ) => {
    try {
      const response = await authService.login(email, password);
      const { access, refresh } = response.data;

      // Store tokens and email
      localStorage.setItem("token", access);
      localStorage.setItem("refreshToken", refresh);
      localStorage.setItem("userEmail", email);

      // Return user info
      return {
        email,
        name: email.split("@")[0], // Temporary name from email
      };
    } catch (error: any) {
      return rejectWithValue(error.response?.data?.detail || "Login failed");
    }
  },
);

export const registerUser = createAsyncThunk(
  "auth/registerUser",
  async (userData: any, { rejectWithValue }) => {
    try {
      // Register the user
      await authService.register(userData);

      // Immediately login after registration
      const loginResponse = await authService.login(
        userData.email,
        userData.password,
      );
      const { access, refresh } = loginResponse.data;

      // Store tokens and email
      localStorage.setItem("token", access);
      localStorage.setItem("refreshToken", refresh);
      localStorage.setItem("userEmail", userData.email);

      return {
        email: userData.email,
        name: userData.email.split("@")[0],
      };
    } catch (error: any) {
      return rejectWithValue(
        error.response?.data?.error || "Registration failed",
      );
    }
  },
);

export const logoutUser = createAsyncThunk(
  "auth/logoutUser",
  async (_, { rejectWithValue }) => {
    try {
      await authService.logout();

      localStorage.removeItem("token");
      localStorage.removeItem("refreshToken");
      localStorage.removeItem("userEmail");

      return null;
    } catch (error: any) {
      return rejectWithValue(error.response?.data?.detail || "Logout failed");
    }
  },
);

export const checkAuthStatus = createAsyncThunk(
  "auth/checkAuthStatus",
  async (_, { rejectWithValue }) => {
    const token = localStorage.getItem("token");
    const refreshToken = localStorage.getItem("refreshToken");

    if (token && refreshToken) {
      try {
        // Verify token (you might want to add a token verification endpoint)
        const email = localStorage.getItem("userEmail");
        return {
          email: email || "",
          name: email ? email.split("@")[0] : "",
        };
      } catch (error) {
        // Token is invalid, clear tokens
        localStorage.removeItem("token");
        localStorage.removeItem("refreshToken");
        localStorage.removeItem("userEmail");
        return rejectWithValue("Invalid token");
      }
    }
    return rejectWithValue("No token");
  },
);

const authSlice = createSlice({
  name: "auth",
  initialState,
  reducers: {
    clearError(state) {
      state.error = null;
    },
    logout(state) {
      state.user = null;
      state.isAuthenticated = false;
      localStorage.removeItem("token");
      localStorage.removeItem("refreshToken");
      localStorage.removeItem("userEmail");
    },
  },
  extraReducers: (builder) => {
    builder
      // Login reducers
      .addCase(loginUser.pending, (state) => {
        state.isLoading = true;
        state.error = null;
      })
      .addCase(loginUser.fulfilled, (state, action) => {
        state.isLoading = false;
        state.isAuthenticated = true;
        state.user = action.payload;
      })
      .addCase(loginUser.rejected, (state, action) => {
        state.isLoading = false;
        state.isAuthenticated = false;
        state.error = action.payload as string;
      })

      // Register reducers
      .addCase(registerUser.pending, (state) => {
        state.isLoading = true;
        state.error = null;
      })
      .addCase(registerUser.fulfilled, (state, action) => {
        state.isLoading = false;
        state.isAuthenticated = true;
        state.user = action.payload;
      })
      .addCase(registerUser.rejected, (state, action) => {
        state.isLoading = false;
        state.isAuthenticated = false;
        state.error = action.payload as string;
      })

      // Logout reducers
      .addCase(logoutUser.fulfilled, (state) => {
        state.isLoading = false;
        state.isAuthenticated = false;
        state.user = null;
      })

      // Check auth status reducers
      .addCase(checkAuthStatus.fulfilled, (state, action) => {
        state.isAuthenticated = true;
        state.user = {
          email: action.payload.email,
          name: action.payload.name,
        };
        state.error = null;
        state.isLoading = false;
      })
      .addCase(checkAuthStatus.rejected, (state) => {
        state.isAuthenticated = false;
        state.user = null;
        state.error = null;
        state.isLoading = false;
      });
  },
});

export const { clearError, logout } = authSlice.actions;
export default authSlice.reducer;
