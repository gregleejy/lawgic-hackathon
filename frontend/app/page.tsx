"use client";

import { useState } from "react";
import { Card, CardHeader, CardTitle, CardContent } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Avatar, AvatarFallback, AvatarImage } from "@/components/ui/avatar";
import { Badge } from "@/components/ui/badge";
import { Switch } from "@/components/ui/switch";

export default function Home() {
  const [enabled, setEnabled] = useState(false);
  const [input, setInput] = useState("");

  return (
    <div className="min-h-screen flex flex-col items-center justify-center bg-gradient-to-br from-blue-100 to-purple-200">
      <Card className="w-full max-w-md shadow-xl">
        <CardHeader className="flex flex-row items-center gap-4">
          <Avatar>
            <AvatarImage src="https://randomuser.me/api/portraits/men/32.jpg" />
            <AvatarFallback>JD</AvatarFallback>
          </Avatar>
          <div>
            <CardTitle className="text-xl">Welcome to Lawgic</CardTitle>
            <Badge variant="outline" className="mt-1">
              PDPA Demo
            </Badge>
          </div>
        </CardHeader>
        <CardContent>
          <div className="mb-4">
            <Input
              placeholder="Type something fun..."
              value={input}
              onChange={(e) => setInput(e.target.value)}
            />
          </div>
          <div className="flex items-center gap-2 mb-4">
            <Switch checked={enabled} onCheckedChange={setEnabled} />
            <span>{enabled ? "Enabled" : "Disabled"}</span>
          </div>
          <Button
            className="w-full"
            onClick={() =>
              setInput("🎉 " + Math.random().toString(36).substring(2, 8))
            }
          >
            Randomize
          </Button>
        </CardContent>
      </Card>
    </div>
  );
}
