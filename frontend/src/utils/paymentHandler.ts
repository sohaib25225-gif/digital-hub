/**
 * Payment Flow Handler (Phase 6 Stage 7)
 *
 * Handles Safepay payment session responses and determines next actions.
 *
 * IMPORTANT: This is a conservative implementation that does NOT fabricate
 * payment integrations. It only handles what the backend provides.
 */

import { CreatePurchaseResponse } from '../types/purchase';

export interface PaymentHandlerResult {
  success: boolean;
  action: 'redirect' | 'sdk_init' | 'error' | 'not_configured';
  message: string;
  data?: {
    url?: string;
    capture_context?: string;
    tracker_token?: string;
  };
}

/**
 * Handles payment session response from backend.
 *
 * Phase 6 Stage 7: Conservative implementation
 * - Detects what payment flow is available
 * - Does NOT fabricate Cybersource integration without capture context
 * - Returns clear error messages for unconfigured flows
 */
export function handlePaymentResponse(response: CreatePurchaseResponse): PaymentHandlerResult {
  const { next_actions, tracker_token, message } = response;

  // Check if next_actions are provided
  if (!next_actions) {
    return {
      success: false,
      action: 'not_configured',
      message: 'Payment flow not configured. No next actions provided.',
    };
  }

  // Handle CYBERSOURCE flow
  if (next_actions.CYBERSOURCE) {
    const cybersourceAction = next_actions.CYBERSOURCE;

    if (cybersourceAction.kind === 'GENERATE_CAPTURE_CONTEXT') {
      // Check if capture context is provided
      if (cybersourceAction.capture_context) {
        // Capture context JWT provided - could initialize Cybersource SDK
        // NOT IMPLEMENTED: Requires Cybersource SDK integration
        return {
          success: false,
          action: 'not_configured',
          message: 'Cybersource payment UI not yet implemented. Capture context received but SDK not loaded.',
          data: {
            capture_context: cybersourceAction.capture_context,
            tracker_token,
          },
        };
      } else {
        // Capture context NOT provided - needs backend endpoint or manual config
        return {
          success: false,
          action: 'not_configured',
          message: 'Payment system requires additional configuration. Capture context generation not implemented.',
          data: {
            tracker_token,
          },
        };
      }
    } else {
      // Unknown CYBERSOURCE action kind
      return {
        success: false,
        action: 'error',
        message: `Unknown Cybersource action: ${cybersourceAction.kind}`,
      };
    }
  }

  // Check if a direct checkout URL is provided (legacy/simple flow)
  if ((response as any).checkout_url) {
    return {
      success: true,
      action: 'redirect',
      message: 'Redirecting to payment page...',
      data: {
        url: (response as any).checkout_url,
        tracker_token,
      },
    };
  }

  // No recognized payment flow
  return {
    success: false,
    action: 'not_configured',
    message: message || 'Payment flow not configured.',
  };
}

/**
 * Poll purchase status from backend.
 *
 * After payment completion (or timeout), refresh purchase status
 * instead of trusting frontend state.
 */
export async function pollPurchaseStatus(
  purchaseId: string,
  getPurchase: (id: string) => Promise<any>,
  maxAttempts: number = 10,
  intervalMs: number = 3000
): Promise<'completed' | 'pending' | 'failed' | 'timeout'> {
  for (let attempt = 0; attempt < maxAttempts; attempt++) {
    try {
      const purchase = await getPurchase(purchaseId);

      if (purchase.status === 'completed') {
        return 'completed';
      }

      if (purchase.status === 'failed') {
        return 'failed';
      }

      // Still pending, wait and retry
      if (attempt < maxAttempts - 1) {
        await new Promise(resolve => setTimeout(resolve, intervalMs));
      }
    } catch (error) {
      console.error('Failed to poll purchase status:', error);
      // Continue polling on error
    }
  }

  return 'timeout';
}
