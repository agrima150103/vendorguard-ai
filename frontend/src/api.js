const API_BASE_URL =
  import.meta.env.VITE_API_BASE_URL ||
  "http://127.0.0.1:8000/api/v1";


async function request(
  endpoint,
  options = {},
) {
  const response = await fetch(
    `${API_BASE_URL}${endpoint}`,
    {
      headers: {
        "Content-Type": "application/json",
        ...(options.headers || {}),
      },
      ...options,
    },
  );

  let responseData = null;

  try {
    responseData = await response.json();
  } catch {
    responseData = null;
  }

  if (!response.ok) {
    const errorMessage =
      responseData?.detail ||
      responseData?.message ||
      `Request failed with status ${response.status}.`;

    throw new Error(errorMessage);
  }

  return responseData;
}


export async function getVendors() {
  return request("/vendors");
}


export async function startAssessment(
  vendorId,
) {
  return request(
    "/assessments",
    {
      method: "POST",
      body: JSON.stringify({
        vendor_id: vendorId,
      }),
    },
  );
}


export async function getAssessment(
  assessmentId,
) {
  if (!assessmentId) {
    throw new Error(
      "Assessment ID is required.",
    );
  }

  return request(
    `/assessments/${encodeURIComponent(
      assessmentId,
    )}`,
  );
}


export async function getAssessments() {
  return request("/assessments");
}


export async function submitReview(
  assessmentId,
  reviewData,
) {
  if (!assessmentId) {
    throw new Error(
      "Assessment ID is required.",
    );
  }

  return request(
    `/assessments/${encodeURIComponent(
      assessmentId,
    )}/review`,
    {
      method: "POST",
      body: JSON.stringify({
        reviewer_id:
          reviewData.reviewer_id ||
          "demo-reviewer",
        decision: reviewData.decision,
        reason: reviewData.reason,
        conditions:
          reviewData.conditions || [],
      }),
    },
  );
}

