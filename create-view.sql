CREATE VIEW `your-project-id.dataset.customer_courier_conversations_view` AS
SELECT
  o.orderId AS order_id,
  o.cityCode AS city_code,
  MIN(CASE
      WHEN m.senderAppType LIKE '%Courier%' THEN m.messageSentTime
  END) AS first_courier_message,
  MIN(CASE
      WHEN m.senderAppType LIKE '%Customer%' THEN m.messageSentTime
  END) AS first_customer_message,
  COUNT(CASE
      WHEN m.senderAppType LIKE '%Courier%' THEN 1
  END) AS num_messages_courier,
  COUNT(CASE
      WHEN m.senderAppType LIKE '%Customer%' THEN 1
  END) AS num_messages_customer,
  CASE
    WHEN MIN(CASE
              WHEN m.senderAppType LIKE '%Courier%' AND m.chatStartedByMessage = true THEN m.senderAppType
              WHEN m.senderAppType LIKE '%Customer%' AND m.chatStartedByMessage = true THEN m.senderAppType
          END) LIKE '%Customer%' THEN 'Customer'
    WHEN MIN(CASE
              WHEN m.senderAppType LIKE '%Courier%' AND m.chatStartedByMessage = true THEN m.senderAppType
              WHEN m.senderAppType LIKE '%Customer%' AND m.chatStartedByMessage = true THEN m.senderAppType
          END) LIKE '%Courier%' THEN 'Courier'
    ELSE 'Unknown'
  END AS first_message_by,
  MIN(m.messageSentTime) AS conversation_started_at,
  ABS(TIMESTAMP_DIFF(
    MIN(CASE
        WHEN m.senderAppType LIKE '%Customer%' THEN m.messageSentTime
    END),
    MIN(CASE
        WHEN m.senderAppType LIKE '%Courier%' THEN m.messageSentTime
    END),
    SECOND
  )) AS first_responsetime_delay_seconds,
  MAX(m.messageSentTime) AS last_message_time,
  last_stage_table.orderStage AS last_message_order_stage
FROM
  `your-project-id.dataset.orders` AS o
JOIN
  `your-project-id.dataset.conversations` AS m
ON
  o.orderId = m.orderId
LEFT JOIN (
  SELECT
    orderId,
    messageSentTime,
    orderStage
  FROM (
    SELECT
      orderId,
      messageSentTime,
      orderStage,
      ROW_NUMBER() OVER (PARTITION BY orderId ORDER BY messageSentTime DESC) as rn
    FROM
      `your-project-id.dataset.conversations`
  ) WHERE rn = 1
) AS last_stage_table
ON
  o.orderId = last_stage_table.orderId
GROUP BY
  o.orderId,
  o.cityCode,
  last_stage_table.orderStage;
