import React, { useState } from 'react';
import { useAuth } from '@/contexts/AuthContext';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Card, CardHeader, CardTitle, CardDescription, CardContent, CardFooter } from '@/components/ui/card';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { Label } from '@/components/ui/label';
import { BarChart3, Loader2, Copy, CheckCircle } from 'lucide-react';
import { toast } from 'sonner';

const AuthScreen: React.FC = () => {
  const { login, signup, loading } = useAuth();
  const [loginInput, setLoginInput] = useState('');
  const [signupName, setSignupName] = useState('');
  const [newUserId, setNewUserId] = useState('');
  const [copied, setCopied] = useState(false);

  const handleLogin = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!loginInput.trim()) return;

    const success = await login(loginInput.trim());
    if (!success) {
      toast.error('Login failed. Please check your name or ID.');
    } else {
      toast.success('Welcome back to InsightIQ!');
    }
  };

  const handleSignup = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!signupName.trim()) return;

    const result = await signup(signupName.trim());
    if (result.success) {
      setNewUserId(result.userId);
      toast.success('Account created successfully!');
    } else {
      toast.error('Failed to create account. Please try again.');
    }
  };

  const copyUserId = () => {
    navigator.clipboard.writeText(newUserId);
    setCopied(true);
    toast.success('User ID copied to clipboard!');
    setTimeout(() => setCopied(false), 2000);
  };

  if (newUserId) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-slate-900 to-slate-800 flex items-center justify-center p-4" data-id="hiax2h722" data-path="src/components/AuthScreen.tsx">
        <Card className="w-full max-w-md" data-id="49rjipb1c" data-path="src/components/AuthScreen.tsx">
          <CardHeader className="text-center" data-id="579psj478" data-path="src/components/AuthScreen.tsx">
            <div className="w-16 h-16 rounded-full bg-green-100 dark:bg-green-900 flex items-center justify-center mx-auto mb-4" data-id="8l8zg0l7l" data-path="src/components/AuthScreen.tsx">
              <CheckCircle className="w-8 h-8 text-green-600 dark:text-green-400" data-id="0qopfhy33" data-path="src/components/AuthScreen.tsx" />
            </div>
            <CardTitle className="text-2xl" data-id="ez63s8bsj" data-path="src/components/AuthScreen.tsx">Welcome to InsightIQ!</CardTitle>
            <CardDescription data-id="zxabjot4t" data-path="src/components/AuthScreen.tsx">Your account has been created successfully</CardDescription>
          </CardHeader>
          <CardContent className="space-y-4" data-id="z50ozys8t" data-path="src/components/AuthScreen.tsx">
            <div className="p-4 bg-muted rounded-lg" data-id="v2cpp69dq" data-path="src/components/AuthScreen.tsx">
              <Label className="text-sm font-medium" data-id="52m0buhq6" data-path="src/components/AuthScreen.tsx">Your User ID</Label>
              <div className="flex items-center space-x-2 mt-2" data-id="d48876dhg" data-path="src/components/AuthScreen.tsx">
                <code className="flex-1 p-2 bg-background rounded border text-lg font-mono" data-id="02buardf7" data-path="src/components/AuthScreen.tsx">
                  {newUserId}
                </code>
                <Button size="sm" variant="outline" onClick={copyUserId} data-id="9vskw8kh3" data-path="src/components/AuthScreen.tsx">
                  {copied ? <CheckCircle className="w-4 h-4" data-id="6i7w1o5d7" data-path="src/components/AuthScreen.tsx" /> : <Copy className="w-4 h-4" data-id="e2l13iwjx" data-path="src/components/AuthScreen.tsx" />}
                </Button>
              </div>
            </div>
            <div className="text-sm text-muted-foreground space-y-2" data-id="5nifk0qs2" data-path="src/components/AuthScreen.tsx">
              <p data-id="w2udedeb8" data-path="src/components/AuthScreen.tsx">• Save this ID - you'll need it to log in</p>
              <p data-id="xsri84q6u" data-path="src/components/AuthScreen.tsx">• You can also log in using your name</p>
              <p data-id="wq0lgokgm" data-path="src/components/AuthScreen.tsx">• Keep this ID secure and don't share it</p>
            </div>
          </CardContent>
          <CardFooter data-id="5exldyzn4" data-path="src/components/AuthScreen.tsx">
            <Button
              className="w-full"
              onClick={() => {
                setNewUserId('');
                setSignupName('');
              }} data-id="hmq44wkuf" data-path="src/components/AuthScreen.tsx">

              Continue to Dashboard
            </Button>
          </CardFooter>
        </Card>
      </div>);

  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-900 to-slate-800 flex items-center justify-center p-4" data-id="22bdwac3h" data-path="src/components/AuthScreen.tsx">
      <Card className="w-full max-w-md" data-id="i0l8937az" data-path="src/components/AuthScreen.tsx">
        <CardHeader className="text-center" data-id="uz7o7bqzz" data-path="src/components/AuthScreen.tsx">
          <div className="w-16 h-16 rounded-full bg-primary/10 flex items-center justify-center mx-auto mb-4" data-id="ht631iriz" data-path="src/components/AuthScreen.tsx">
            <BarChart3 className="w-8 h-8 text-primary" data-id="ihryt74px" data-path="src/components/AuthScreen.tsx" />
          </div>
          <CardTitle className="text-2xl" data-id="fzzp94jdc" data-path="src/components/AuthScreen.tsx">InsightIQ</CardTitle>
          <CardDescription data-id="ar8re5mh4" data-path="src/components/AuthScreen.tsx">Business Intelligence Automation & Analysis Portal</CardDescription>
        </CardHeader>
        <CardContent data-id="8fj7w04w6" data-path="src/components/AuthScreen.tsx">
          <Tabs defaultValue="login" className="space-y-4" data-id="n5r5oqzau" data-path="src/components/AuthScreen.tsx">
            <TabsList className="grid w-full grid-cols-2" data-id="7q6lrekvi" data-path="src/components/AuthScreen.tsx">
              <TabsTrigger value="login" data-id="1w48akm6t" data-path="src/components/AuthScreen.tsx">Login</TabsTrigger>
              <TabsTrigger value="signup" data-id="e4vdwn0le" data-path="src/components/AuthScreen.tsx">Sign Up</TabsTrigger>
            </TabsList>
            
            <TabsContent value="login" data-id="9fvw1yaz9" data-path="src/components/AuthScreen.tsx">
              <form onSubmit={handleLogin} className="space-y-4" data-id="pityeben5" data-path="src/components/AuthScreen.tsx">
                <div className="space-y-2" data-id="o96vu75ie" data-path="src/components/AuthScreen.tsx">
                  <Label htmlFor="login-input" data-id="u5oljauh2" data-path="src/components/AuthScreen.tsx">Name or 8-digit ID</Label>
                  <Input
                    id="login-input"
                    type="text"
                    placeholder="Enter your name or ID"
                    value={loginInput}
                    onChange={(e) => setLoginInput(e.target.value)}
                    disabled={loading} data-id="rvc6r753r" data-path="src/components/AuthScreen.tsx" />

                </div>
                <Button type="submit" className="w-full" disabled={loading || !loginInput.trim()} data-id="qk9ojg983" data-path="src/components/AuthScreen.tsx">
                  {loading ?
                  <>
                      <Loader2 className="w-4 h-4 mr-2 animate-spin" data-id="3vk6obw0j" data-path="src/components/AuthScreen.tsx" />
                      Logging in...
                    </> :

                  'Login'
                  }
                </Button>
              </form>
            </TabsContent>
            
            <TabsContent value="signup" data-id="vq3iox01v" data-path="src/components/AuthScreen.tsx">
              <form onSubmit={handleSignup} className="space-y-4" data-id="fmaftxxe8" data-path="src/components/AuthScreen.tsx">
                <div className="space-y-2" data-id="p5bnl1mvk" data-path="src/components/AuthScreen.tsx">
                  <Label htmlFor="signup-name" data-id="r9dcx48gy" data-path="src/components/AuthScreen.tsx">Your Name</Label>
                  <Input
                    id="signup-name"
                    type="text"
                    placeholder="Enter your full name"
                    value={signupName}
                    onChange={(e) => setSignupName(e.target.value)}
                    disabled={loading} data-id="vgta77x66" data-path="src/components/AuthScreen.tsx" />

                </div>
                <div className="text-sm text-muted-foreground" data-id="5mma0kprd" data-path="src/components/AuthScreen.tsx">
                  We'll generate a unique 8-digit ID for you automatically.
                </div>
                <Button type="submit" className="w-full" disabled={loading || !signupName.trim()} data-id="ddc8bik31" data-path="src/components/AuthScreen.tsx">
                  {loading ?
                  <>
                      <Loader2 className="w-4 h-4 mr-2 animate-spin" data-id="vyulcfzvl" data-path="src/components/AuthScreen.tsx" />
                      Creating Account...
                    </> :

                  'Create Account'
                  }
                </Button>
              </form>
            </TabsContent>
          </Tabs>
        </CardContent>
      </Card>
    </div>);

};

export default AuthScreen;