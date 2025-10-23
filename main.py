
from agents.inventory_agent import run_inventory_agent

run_inventory_agent(
    '''
    check our inventory, identify low stock items where sum(quantity) below threshold level, 
    search for suppliers for our low stock items if there is any lowstock item.
    send me an email summary of the low stock items and the suppliers with links. 
    If there is no low stock item, just send me an email saying all items are sufficiently stocked.
    '''
)

"""
if __name__ == "__main__":
    print("Smart Inventory Agent (conversational). Type 'exit' to quit.")
    while True:
        try:
            user_q = input("You: ").strip()
        except EOFError:
            break
        if not user_q:
            continue
        if user_q.lower() in {"exit", "quit"}:
            print("Assistant: Bye!")
            break
        answer = run_conversational_agent(user_q)
        print(f"Assistant: {answer}")

"""