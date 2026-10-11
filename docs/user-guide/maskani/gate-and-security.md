# Gate and security

## Passes

Residents create gate passes on the portal: a single visit, a recurring guest, domestic staff, a
delivery or a contractor. The visitor gets a gate code by WhatsApp. Staff can create passes from the
console too.

## The guard tablet

A tablet at the gate is set up once by the office and then signed into by each guard with a PIN at
the start of the shift. The guard:

- **checks a pass** by its code or QR and lets the visitor in,
- **records a walk-in** for someone without a pass, with name, phone, host unit and vehicle,
- **records the exit** of someone inside,
- sees **who is inside now**, with which guard let them in at which gate.

The tablet keeps working when the internet drops and catches up when it is back.

```mermaid
flowchart TD
  V[Visitor at the gate] --> P{Has a pass?}
  P -- yes --> C[Guard checks the code] --> IN[Entry recorded]
  P -- no --> W[Guard records a walk-in]
  W --> POL{Estate policy}
  POL -- guard decides --> IN
  POL -- ask the host --> RING[Ring the resident:<br/>push to their phone]
  RING -- let in --> IN
  RING -- declined --> OUT[Turned away]
  IN --> EX[Exit recorded later]
```

## Walk-in policy

Under **Settings, General** choose whether the guard decides walk-ins (the host is told who came in)
or the host must answer first. Either way the guard can **ring** the resident, which pushes an alert
to their phone with let in or decline buttons. For the push to reach them, residents open the portal
on their phone once and allow notifications; on an iPhone they add the portal to the Home Screen
first.

## Returning visitors

Maskani remembers visitors by phone, ID and number plate, so a regular visitor is recognised and the
guard's form fills itself.

## Incidents

Guards and staff record incidents with a category, severity and photos. Serious incidents alert the
security manager straight away.
