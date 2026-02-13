import React from "react";
import { getCompanyAnalytics } from "../api/productApi";

export default function CompanyInsights({ company }) {

  const fetchData = async () => {
    const res = await getCompanyAnalytics(company);
    console.log(res.data);
  };

  return (
    <button onClick={fetchData}>
      View Company Insights
    </button>
  );
}
