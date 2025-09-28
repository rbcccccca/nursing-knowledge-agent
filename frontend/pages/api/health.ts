import type { NextApiRequest, NextApiResponse } from "next";

const handler = (_request: NextApiRequest, response: NextApiResponse) => {
  response.status(200).json({ status: "ok" });
};

export default handler;
