# Inventory Management Policies and overview of our model

Inventory policies are strategies for managing the amount of inventory a company has on hand in order to meet customer demand. 
There are different inventory policies that a company can use, and the choice of policy depends on factors such as the *type of product*, 
the *lead time for ordering*, and *the cost of holding inventory*. 

Here are some common inventory policies, along with their mathematical formulas.

- #### Economic Order Quantity (EOQ)
This policy seeks to minimize the total cost of ordering and holding inventory. The formula for EOQ is: sqrt((2 x D x S) / H), where D is the annual demand, S is the ordering cost, and H is the holding cost per unit.

- #### (Q,R) Policy
This policy involves ordering a fixed quantity Q of inventory when the inventory level reaches a reorder point R. The formula for calculating R is: R = D x L, where D is the daily demand and L is the lead time for ordering.

- #### Just-In-Time (JIT)

This policy seeks to minimize inventory levels by only ordering inventory when it is needed. This requires a high degree of coordination with suppliers and a reliable supply chain.

- #### Safety Stock
This policy involves holding a certain amount of extra inventory to cover unexpected demand or supply chain disruptions. The formula for calculating safety stock is: Z x σ x sqrt(L), where Z is the desired service level, σ is the standard deviation of demand during lead time, and L is the lead time.

Overall, choosing the right inventory policy can help a company maintain the right level of inventory to meet customer demand while minimizing costs and optimizing the supply chain.

---

## Our model: a (Q,R) inventory model

In this Solution Accelerator, we provide a simplified (Q,R) inventory model as an integer programming model, based on the article published [here](http://yetanothermathprogrammingconsultant.blogspot.com/2020/11/optimal-qr-inventory-policy-as-mip.html).

> The (Q,R) inventory policy is a way to manage inventory. When the inventory falls below a certain level, called R, an order for a specific quantity, called Q, is placed. 
> This model also takes into account lead times, which is the time it takes for an order to be delivered. When inventory reaches zero, any additional demand creates a backlog. This backlog will be fulfilled when replenishments arrive, but at a cost.
> There are different types of costs involved in this model. There is a fixed ordering cost, which is the cost of placing an order. There is also a holding cost related to keeping inventory on hand. Finally, there are penalties related to backlogs, which are costs incurred due to customers waiting for their orders to be fulfilled.

#### Model Definition

Decision Variables


- $Q$ is the reorder quantity, which represents the size of each order placed. $0 \leq Q \leq maxQ$, where $maxQ$ is the maximum allowed reorder quantity.

- $R$ is the reorder point, which represents the inventory level at which we place an order. The expression is $0 \leq R \leq invCap$, where $invCap$ is the maximum inventory capacity.
- $invT$ is the inventory level at the end of period $t$. The expression is $0 \leq invT \leq invCap$, where $invCap$ is the maximum inventory capacity.
- $backT$ is the backlog demand, which represents the unfulfilled demand we satisfy once new inventory arrives, at the end of period $t$. The expression is $0 \leq backT \leq maxBackLogged$, where $maxBackLogged$ is the maximum allowed backlog demand.
- $\text{lowInv} \in \{0,1\}$ represents the boolean variable that indicates whether the inventory level is low or not.
- $\text{lowT} \in \{0,1\}$ represents the boolean variable that indicates whether the inventory level is low or not at times t.
- $\text{orderT} \in \{0,1\}$ represents the boolean variable that indicates whether an order is placed or not. An order is placed when the inventory level, $\text{invT}$, drops below $\text{R}$.
- $\text{replT}$ represents the replenishment of the inventory at the end of period $\text{t}$. It can be used to fulfill backlogged demand and is equal to the reorder quantity $\text{Q}$ or zero.

Here are the equations of our model:


1. The objective function can be written as:

$$z = F + H + B$$

where:
- $F$ is the fixed ordering cost
- $H$ is the holding cost
- $B$ is the backlog penalties

The goal is to minimize $z$, which represents the total cost of managing inventory.

2. The inventory balance equation is a bit complex as we allow backlog:

The inventory balance equation with backlog can be expressed as:

$invT_{t} = invT_{t-1} + replT_{t-1} - backT_{t-1} - D_{t} + lowInv_{t-1}$

where $D_{t}$ is the demand in period $t$, and $lowInv_{t-1}$ is a boolean variable indicating if the inventory level was low at the end of period $t-1$.

This equation states that the inventory level at the end of period $t$ is equal to the inventory level at the end of the previous period plus the replenishment quantity from the previous period minus the backlog demand from the previous period minus the demand in the current period, plus a binary variable that indicates whether the inventory level was low at the end of the previous period.

Using the decision variables and parameters given, the objective function can be expressed as:

$z = F \cdot orderT_{t} + H \cdot invT_{t} + B \cdot backT_{t}$

where $F$ is the fixed ordering cost, $H$ is the holding cost related to inventory, and $B$ is the penalties related to backlogs, and $orderT_{t}$ is the boolean variable indicating whether an order was placed in period $t$.

---
3. To add the low inventory equation, 

where $lowThres$ is the threshold inventory level below which the inventory level is considered low.

4. To add the reorder event equation, we can define a new boolean variable, $\text{reorderT}$, which indicates whether a reorder event took place in period $t$:

This equation states that a reorder event occurs in period $t$ if the inventory level was at or above the reorder point, $R$, at the end of the previous period, but drops below the reorder point at the end of period $t$.

5. The inventory replenishment takes place after an order was placed and when the lead time passed. No ordering happened just before the simulation started.

$repl_{t} = Q \cdot orderT_{t-LeadTime}$

