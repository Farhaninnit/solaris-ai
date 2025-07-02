"use client";

import { useState } from "react";
import { Button } from "../ui/button";
import { Textarea } from "../ui/textarea";
import createApiClient from "@/lib/getApiClient";
import { useRouter } from "next/navigation";
import { Loader2 } from "lucide-react";
import { getSessionId } from "@/lib/getUserId";
import {
  Card,
  CardContent,
  CardDescription,
  CardFooter,
  CardHeader,
  CardTitle,
} from "../ui/card";

export default function SubmitQueryForm() {
  const api = createApiClient();
  const userId = getSessionId();
  const originalPlaceHolder: string =
    "What time of the day usually has the most solar power output?";

  const [query, setQuery] = useState("");
  const [isSubmitting, setIsSubmitting] = useState(false);
  const router = useRouter();

  const submitForm = () => {
    const queryToSubmit = query || originalPlaceHolder;
    console.log(`Submitting query: ${queryToSubmit}`);
    const request = { queryText: queryToSubmit, userId: userId };
    const response = api.submitQueryEndpointSubmitQueryPost({
      submitQueryRequest: request,
    });

    setIsSubmitting(true);
    response.then((data) => {
      console.log(data);
      router.push(`/viewQuery?query_id=${data.queryId}`);
    });
  };

  const textArea = (
    <Textarea
      placeholder={originalPlaceHolder}
      value={query}
      disabled={isSubmitting}
      onChange={(e) => {
        setQuery(e.currentTarget.value);
      }}
    />
  );

  const submitButton = (
    <Button onClick={submitForm} disabled={isSubmitting} className="ml-auto">
      {isSubmitting && <Loader2 className="mr-2 h-4 w-4 animate-spin" />} Submit
    </Button>
  );

  return (
    <Card className="w-full">
      <CardHeader>
        <CardTitle>Submit New Query</CardTitle>
        <CardDescription>
          Solaris AI
        </CardDescription>
      </CardHeader>
      <CardContent>
        <div className="w-full">{textArea}</div>
      </CardContent>
      <CardFooter>{submitButton}</CardFooter>
    </Card>
  );
}
