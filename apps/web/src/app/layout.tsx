import Script from "next/script";
import type { ReactNode } from "react";

import "./globals.css";

export const metadata = {
  title: "Commercial Area Analysis MVP",
  description: "Mock-data commercial area analysis service"
};

export default function RootLayout({ children }: { children: ReactNode }) {
  return (
    <html lang="ko">
      <head>
        {process.env.NODE_ENV === "development" ? (
          <>
            <Script
              src="//unpkg.com/react-grab/dist/index.global.js"
              crossOrigin="anonymous"
              strategy="beforeInteractive"
            />
            <Script
              src="//unpkg.com/react-scan/dist/auto.global.js"
              crossOrigin="anonymous"
              strategy="beforeInteractive"
            />
          </>
        ) : null}
      </head>
      <body>{children}</body>
    </html>
  );
}

