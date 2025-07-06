import React, { createContext, useContext, useEffect, useState } from 'react';
import { supabase } from '@/lib/supabase';

interface User {
  id: string;
  user_id: string;
  name: string;
  created_at: string;
}

interface AuthContextType {
  user: User | null;
  loading: boolean;
  login: (nameOrId: string) => Promise<boolean>;
  signup: (name: string) => Promise<{success: boolean;userId: string;}>;
  logout: () => void;
  regenerateId: () => Promise<string>;
}

const AuthContext = createContext<AuthContextType | undefined>(undefined);

export const useAuth = () => {
  const context = useContext(AuthContext);
  if (context === undefined) {
    throw new Error('useAuth must be used within an AuthProvider');
  }
  return context;
};

const generateUserId = (): string => {
  return Math.floor(10000000 + Math.random() * 90000000).toString();
};

export const AuthProvider: React.FC<{children: React.ReactNode;}> = ({ children }) => {
  const [user, setUser] = useState<User | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    // Check if user is logged in from localStorage
    const savedUser = localStorage.getItem('insightiq_user');
    if (savedUser) {
      setUser(JSON.parse(savedUser));
    }
    setLoading(false);
  }, []);

  const login = async (nameOrId: string): Promise<boolean> => {
    try {
      setLoading(true);

      // Check if input is 8-digit ID or name
      const isId = /^\d{8}$/.test(nameOrId);

      const { data, error } = await supabase.
      from('app_users').
      select('*').
      eq(isId ? 'user_id' : 'name', nameOrId).
      single();

      if (error || !data) {
        return false;
      }

      setUser(data);
      localStorage.setItem('insightiq_user', JSON.stringify(data));
      return true;
    } catch (error) {
      console.error('Login error:', error);
      return false;
    } finally {
      setLoading(false);
    }
  };

  const signup = async (name: string): Promise<{success: boolean;userId: string;}> => {
    try {
      setLoading(true);
      const userId = generateUserId();

      // Check if user ID already exists (very unlikely but safe)
      const { data: existingUser } = await supabase.
      from('app_users').
      select('user_id').
      eq('user_id', userId).
      single();

      if (existingUser) {
        // Regenerate if collision
        return signup(name);
      }

      const { data, error } = await supabase.
      from('app_users').
      insert([
      {
        user_id: userId,
        name: name.trim()
      }]
      ).
      select().
      single();

      if (error) {
        console.error('Signup error:', error);
        return { success: false, userId: '' };
      }

      setUser(data);
      localStorage.setItem('insightiq_user', JSON.stringify(data));
      return { success: true, userId };
    } catch (error) {
      console.error('Signup error:', error);
      return { success: false, userId: '' };
    } finally {
      setLoading(false);
    }
  };

  const logout = () => {
    setUser(null);
    localStorage.removeItem('insightiq_user');
  };

  const regenerateId = async (): Promise<string> => {
    if (!user) return '';

    try {
      const newUserId = generateUserId();

      const { data, error } = await supabase.
      from('app_users').
      update({ user_id: newUserId }).
      eq('id', user.id).
      select().
      single();

      if (error) {
        console.error('ID regeneration error:', error);
        return '';
      }

      setUser(data);
      localStorage.setItem('insightiq_user', JSON.stringify(data));
      return newUserId;
    } catch (error) {
      console.error('ID regeneration error:', error);
      return '';
    }
  };

  const value = {
    user,
    loading,
    login,
    signup,
    logout,
    regenerateId
  };

  return <AuthContext.Provider value={value} data-id="5y068s03t" data-path="src/contexts/AuthContext.tsx">{children}</AuthContext.Provider>;
};